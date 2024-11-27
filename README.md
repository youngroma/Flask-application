Prerequisites:

Before setting up the application, ensure you have the following:

- Python 3.10+ installed on your machine
- Docker installed on your machine
- An OpenAI API key

Setup Instructions

1. Create a .env file in the project root with your data:
   
<p>SECRET_KEY=your_secret_key</p>
<p>DATABASE_URL=postgresql://yourname_of_user:your_password@localhost/name_of_database</p>
<p>GOOGLE_CLIENT_ID=your_google_client_id</p>
<p>GOOGLE_CLIENT_SECRET=your_google_client_secret_key</p>

OPENAI_API_KEY=your_openai_api_key

2. Clone Repo
   
git clone <repository_url>

cd <project_directory>

3. Build Docker image
   
docker build -t myapp .

docker run -p 5000:5000 myapp





Photos of web-app:

![image](https://github.com/user-attachments/assets/16459693-6c72-4561-9e12-d28634ff4a94)
![image](https://github.com/user-attachments/assets/7f16a919-63e8-45a3-90cb-79b48af2ed14)
![image](https://github.com/user-attachments/assets/775ee051-7ba9-4746-953f-81907bc197d5)
![image](https://github.com/user-attachments/assets/bc812bcc-4e35-49ad-8818-4a0f7e3a61f2)


