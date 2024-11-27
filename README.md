Prerequisites:

Before setting up the application, ensure you have the following:

- Python 3.10+ installed on your machine
- Docker installed on your machine
- An OpenAI API key

Setup Instructions

1. Create a .env file in the project root with your data:
   
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://yourname_of_user:your_password@localhost/name_of_database
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret_key
OPENAI_API_KEY=your_openai_api_key

2. Clone Repo
git clone <repository_url>
cd <project_directory>

3. Build Docker image
docker build -t myapp .
docker run -p 5000:5000 myapp
