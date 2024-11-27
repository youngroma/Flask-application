import os

from flask import Blueprint, session, redirect, request, abort, render_template
from modules.web_application.models.models import db, User, ScrapedData
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests
from pip._vendor import cachecontrol
from flask import request, jsonify
from langchain_integration import generate_response
from modules.web_application.models.models import PromptLog, db
from bs4 import BeautifulSoup
from datetime import datetime
from validators import url as validate_url
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask_wtf.csrf import CSRFProtect

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')

@views.route('/login')
def login():
    from app import flow
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

CLIENT_ID = os.getenv("CLIENT_ID") #
@views.route('/callback')
def callback():
    from app import flow
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=CLIENT_ID      #from .env
    )

    google_id = id_info.get("sub")
    name = id_info.get("name")
    email = id_info.get("email")
    profile_picture = id_info.get("picture")
    provider = "google"

    # Проверяем, существует ли пользователь с таким email
    user = User.query.filter_by(email=email).first()

    if user:
        # Если пользователь существует, обновляем его данные
        user.name = name
        user.profile_picture = profile_picture
        user.social_login_provider = provider
    else:
        # Если пользователь не найден, создаем нового
        user = User(name=name, email=email, profile_picture=profile_picture, social_login_provider=provider)
        db.session.add(user)

    db.session.commit()

    # Сохраняем user_id и имя пользователя в сессии
    session["user_id"] = user.id  # Сохраняем user.id в сессии вместо google_id
    session["name"] = name

    return redirect("/protected_area")


@views.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@views.route('/protected_area')
def protected_area():
    if 'google_id' not in session:
        return redirect('/')

    session_name = session.get('name', 'Guest')
    return '''
        <h1>Hello {}</h1>
        <form method="POST" action="/scrape">
            <label for="url">Enter URL to scrape:</label><br>
            <input type="text" id="url" name="url" required><br><br>
            <input type="submit" value="Scrape Data">
        </form>
        <a href='/logout'><button>Logout</button></a>
    '''.format(session_name)


@views.route('/generate', methods=['GET', 'POST'])
def generate_prompt_response():
    # Проверяем, залогинен ли пользователь
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']  # Получаем user_id из сессии

    if request.method == 'GET':
        # Возвращаем HTML-шаблон для формы
        return render_template('generate_prompt.html', user_id=user_id)

    try:
        # Получаем данные из формы
        prompt_text = request.form.get('prompt')

        if not prompt_text:
            return render_template('generate_prompt.html', error='Prompt is required', user_id=user_id)

        # Генерация ответа (замените на свою функцию)
        response, tokens_used = generate_response(prompt_text)

        # Сохраняем в базе данных
        new_log = PromptLog(
            prompt_text=prompt_text,
            generated_output=response,
            created_by_user_id=user_id,
            tokens_used=tokens_used
        )
        db.session.add(new_log)
        db.session.commit()

        # Возвращаем данные на страницу
        return render_template(
            'generate_prompt.html',
            prompt_text=prompt_text,
            response=response,
            tokens_used=tokens_used,
            user_id=user_id
        )

    except Exception as e:
        return render_template('generate_prompt.html', error=str(e), user_id=user_id)



@views.route('/scrape', methods=['POST'])
def scrape_url():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Validate the URL format
    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400

    # Check if the page is JavaScript-heavy
    js_based = False
    soup = None
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for JavaScript-heavy indicators
        if len(soup.find_all('script')) > len(soup.find_all(['p', 'h1', 'meta'])):
            js_based = True

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400

    # Handle JavaScript-heavy websites using Selenium
    if js_based:
        try:
            options = Options()
            options.add_argument('--headless')  # Run browser in headless mode
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=options)

            driver.get(url)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            driver.quit()
        except Exception as e:
            return jsonify({'error': f'Unable to scrape JavaScript-heavy site: {str(e)}'}), 400

    # Extract metadata
    scraped_metadata = {
        'title': soup.title.string if soup.title else "Not available",
        'description': (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', "Not available"),
        'keywords': (soup.find('meta', attrs={'name': 'keywords'}) or {}).get('content', "Not available"),
        'url': url
    }

    # Extract additional information
    name = soup.find('h1').get_text(strip=True) if soup.find('h1') else scraped_metadata['title']
    about = scraped_metadata['description']
    source = "Social Media" if "twitter.com" in url or "facebook.com" in url else "Company/Website"
    industry = (soup.find('meta', attrs={'name': 'industry'}) or {}).get('content', "Not available")
    page_content_type = (soup.find('meta', attrs={'name': 'type'}) or {}).get('content', "Not available")
    contact_links = [a['href'] for a in soup.find_all('a', href=True) if "contact" in a['href'].lower()]
    email_links = [a['href'].replace('mailto:', '') for a in soup.find_all('a', href=True) if "mailto:" in a['href']]
    contact = contact_links[0] if contact_links else "Not available"
    email = email_links[0] if email_links else "Not available"
    page_content = soup.get_text(separator=' ', strip=True)[:1000]

    scraped_data = {
        'name': name,
        'about': about,
        'source': source,
        'industry': industry,
        'page_content_type': page_content_type,
        'contact': contact,
        'email': email,
        'page_content': page_content
    }

    # Save to database
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    scraped_data_entry = ScrapedData(
        url=url,
        content=page_content,
        scraped_metadata=scraped_metadata,
        created_by_user_id=user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(scraped_data_entry)

    db.session.commit()

    return jsonify({
        'message': 'Data scraped successfully',
        'scraped_metadata': scraped_metadata,
        'scraped_data': scraped_data
    }), 200


@views.route('/scrape_page', methods=['GET'])
def scrape_page_view():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('scrape_page.html')

@views.route('/dashboard')
def dashboard():
    # Проверяем, залогинен ли пользователь
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    # Получаем данные, связанные с пользователем
    scraped_data = ScrapedData.query.filter_by(created_by_user_id=user_id).all()
    prompts = PromptLog.query.filter_by(created_by_user_id=user_id).all()

    return render_template('dashboard.html', scraped_data=scraped_data, prompts=prompts)


@views.route('/delete_scraped_data/<int:data_id>', methods=['POST'])
def delete_scraped_data(data_id):
    if 'user_id' not in session:
        return redirect('/login')

    data = ScrapedData.query.get_or_404(data_id)
    if data.created_by_user_id != session['user_id']:
        return "Unauthorized", 403

    db.session.delete(data)
    db.session.commit()
    return redirect('/dashboard')

@views.route('/delete_prompt/<int:prompt_id>', methods=['POST'])
def delete_prompt(prompt_id):
    if 'user_id' not in session:
        return redirect('/login')

    prompt = PromptLog.query.get_or_404(prompt_id)

    # Проверяем, принадлежит ли промпт текущему пользователю
    if prompt.created_by_user_id != session['user_id']:
        return "Unauthorized", 403

    db.session.delete(prompt)
    db.session.commit()
    return redirect('/dashboard')


@views.route('/edit_scraped_data/<int:data_id>', methods=['GET', 'POST'])
def edit_scraped_data(data_id):
    if 'user_id' not in session:
        return redirect('/login')

    data = ScrapedData.query.get(data_id)
    if not data or data.created_by_user_id != session['user_id']:
        return "Unauthorized or data not found", 404

    data = ScrapedData.query.get_or_404(data_id)

    if request.method == 'POST':
        data.url = request.form['url']
        data.scraped_metadata['title'] = request.form['title']
        data.scraped_metadata['description'] = request.form['description']
        data.scraped_metadata['keywords'] = request.form['keywords']
        data.contact = request.form['contact']
        data.email = request.form['email']
        data.content = request.form['content']

        print(data.scraped_metadata)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_scraped_data.html', data=data)


@views.route('/edit_prompt/<int:prompt_id>', methods=['GET', 'POST'])
def edit_prompt(prompt_id):
    if 'user_id' not in session:
        return redirect('/login')

    prompt = PromptLog.query.get_or_404(prompt_id)

    # Проверяем, принадлежит ли промпт текущему пользователю
    if prompt.created_by_user_id != session['user_id']:
        return "Unauthorized", 403

    if request.method == 'POST':
        prompt_text = request.form['prompt_text']
        generated_output = request.form['generated_output']

        if not prompt_text or not generated_output:
            return render_template('edit_prompt.html', prompt=prompt, error="All fields are required.")

        prompt.prompt_text = prompt_text
        prompt.generated_output = generated_output

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_prompt.html', prompt=prompt)









