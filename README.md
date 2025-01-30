# Flask Application

This project is a **Flask-based web application** that integrates **LangChain for AI prompting**, **web scraping**, and **Google OAuth authentication**.

## Technologies Used
- **Flask** – Web framework for handling API requests
- **LangChain** – AI-powered prompting and processing
- **BeautifulSoup** – Web scraping for extracting data
- **OAuth 2.0 (Google Login)** – Secure authentication
- **PostgreSQL** – Database for storing user and application data
- **Docker** – Containerization for deployment

## Before setting up the application, ensure you have the following:

- Python 3.10+ installed on your machine
- Docker installed on your machine
- An OpenAI API key

## Features
- AI Prompting: Uses LangChain to generate responses.
- Web Scraping: Extracts content dynamically.
- User Authentication: Secure login via Google OAuth.
- Database Integration: Uses PostgreSQL for storing user data.

# Setup Instructions

## 1. Create a .env file in the project root with your data:
 ```bash  
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://yourname_of_user:your_password@localhost/name_of_database
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret_key
OPENAI_API_KEY=your_openai_api_key
```
# 2. Clone Repo
```bash
git clone https://github.com/youngroma/Flask-application.git

cd Flask-application
```
# 3. Build Docker image
```bash
docker build -t myapp .

docker run -p 5000:5000 myapp
```



