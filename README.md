# YouTube Blog Summary App

A Python-Django application that allows users to summarize YouTube videos by generating concise scripts from their transcripts. The app integrates audio download, transcription, and AI-based summarization, and stores the results in a database.

---

## Features

1. **User Authentication**
   - Users can create accounts, log in, and log out to manage access securely.

2. **YouTube Audio Download**
   - Users provide a YouTube video link.
   - The app downloads the audio from the video using `yt_dlp`.

3. **Audio Transcription**
   - Converts the downloaded audio into text using `AssemblyAI`.

4. **Summarization**
   - Shortens the transcript to comply with GooseAI's token limit.
   - Generates a script summary using GooseAI's text-generation capabilities.

5. **Database Storage**
   - Saves the following details in an AWS-hosted PostgreSQL database:
     - User
     - YouTube title
     - YouTube link
     - Generated content (summary)
     - Date and time of creation

6. **Post Management**
   - Users can view all the posts they have created in a dedicated dashboard.



## Prerequisites

Before running the application, ensure you have the following:

- Python 3.8+
- Django 4.x
- PostgreSQL Database (AWS-hosted or local)
- API Keys:
   - AssemblyAI API key for transcription services.
   - GooseAI API key for summarization.


## Installation and Setup

1. **Clone the Repository**
```
git clone https://github.com/marcornc/AI_Blog_App.git
cd AI_Blog_App
```

2. **Set Up a Virtual Environment**
```
python -m venv .venv
.venv\Scripts\activate
```

3. **Install Dependencies**
```
pip install -r requirements.txt
```

4. **Configure the Environment**
- Create a .env file in the project root with the following keys:

   - NAME_DB = name of the DB
   - MASTER_USER = name superuser 
   - PASSWORD_DB = DB password
   - DB_HOST = DB host
   - SECRET_KEY = Django secret key
   - AAI_KEY = key for assemblyai
   - GOOSEAI_KEY = key for GooseAI

5. **Set Up the Database**
Apply migrations to set up the PostgreSQL database:
```
python manage.py makemigrations
python manage.py migrate
```

6. **Run the Development Server**
```
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.



## Usage

1. **Sign Up or Log In**
   - Create an account or log in using existing credentials.

2. **Generate a Summary**
   - Input a valid YouTube video link.
   - The app will:
     - Download the audio from the video.
      - Transcribe the audio to text.
      - Summarize the transcription using GooseAI.
      - Save the results in the database.
   
3. **View Saved Posts**
   - Access your dashboard to view all generated summaries, including:
     - YouTube title
      - YouTube link
      - Summary content



## Technologies Used

   - Backend Framework: Django
   - Frontend: HTML, CSS, JavaScript (basic templates)
   - Database: AWS PostgreSQL
   - Audio Download: `yt_dlp`
   - Transcription: `AssemblyAI`
   - Text Generation: GooseAI (OpenAI API alternative)



## API Details

- AssemblyAI
   - Converts audio files to text transcripts.
   - Requires an API key.

- GooseAI
   - Generates script summaries from text.
   - Requires an API key.



## Notes

- Audio Storage: Audio files are temporarily stored in the media/ folder and deleted after processing.
- Token Limit: Transcripts are truncated to fit within GooseAI's token limit to avoid errors.



## Acknowledgements

- AssemblyAI: For transcription services.
- GooseAI: For summarization.
- yt-dlp: For downloading YouTube audio.