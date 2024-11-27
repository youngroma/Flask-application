import requests
from app import create_app
import pytest
from unittest.mock import MagicMock
from flask import url_for

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_google_oauth(mocker):
    mock_oauth = mocker.patch('app.flow')
    return mock_oauth


def test_user_login(mock_google_oauth, app):
    with app.app_context():

        mock_google_oauth.get.return_value = MagicMock(status_code=200)
        response = mock_google_oauth.get(url_for('views.login'))

        assert response.status_code == 200


def test_generate_prompt_get(client):
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/generate')
    assert response.status_code == 200
    assert b"Generate Prompt" in response.data


def test_generate_prompt_post_success(client, mocker):
    with client.session_transaction() as session:
        session['user_id'] = 1

    mock_generate_response = mocker.patch("langchain_integration.generate_response")
    mock_generate_response.return_value = ("Generated Response", 15)

    response = client.post('/generate', data={'prompt': 'Test Prompt'})
    assert response.status_code == 200

    assert b"Generated Response" in response.data  # Validate response text
    assert b"<strong>Tokens Used:</strong> " in response.data  # Match the actual HTML structure


def test_generate_prompt_post_missing_prompt(client):
    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.post('/generate', data={})  # No prompt provided
    assert response.status_code == 200
    assert b"Prompt is required" in response.data


def test_scrape_url_success(client, mocker):
    with client.session_transaction() as session:
        session['user_id'] = 1

    mock_requests = mocker.patch("requests.get")
    mock_response = mock_requests.return_value
    mock_response.status_code = 200
    mock_response.text = "<html><head><title>Test Title</title></head><body><h1>Test Header</h1></body></html>"

    response = client.post('/scrape', data={'url': 'http://example.com'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['scraped_metadata']['title'] == "Test Title"
    assert json_data['scraped_data']['name'] == "Test Header"


def test_scrape_js_heavy_site(client, mocker):
    with client.session_transaction() as session:
        session['user_id'] = 1

    mock_requests = mocker.patch("requests.get")
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.text = "<html><script></script><script></script></html>"  # Simulate JS-heavy page

    mock_selenium = mocker.patch("selenium.webdriver.Chrome")
    mock_driver = mock_selenium.return_value
    mock_driver.page_source = "<html><head><title>JS Title</title></head><body><h1>JS Header</h1></body></html>"

    response = client.post('/scrape', data={'url': 'http://example.com'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['scraped_metadata']['title'] == "JS Title"
    assert json_data['scraped_data']['name'] == "JS Header"


def test_scrape_invalid_url(client):
    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.post('/scrape', data={'url': 'invalid_url'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Invalid URL format"


def test_scrape_url_timeout(client, mocker):
    with client.session_transaction() as session:
        session['user_id'] = 1

    mock_requests = mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    response = client.post('/scrape', data={'url': 'http://example.com'})
    assert response.status_code == 504
    json_data = response.get_json()
    assert json_data['error'] == "Request timed out"







