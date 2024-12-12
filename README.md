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
   - Generates a script summary using GooseAI's text generation capabilities.

5. **Database Storage**
   - Saves the following details in an AWS-hosted PostgreSQL database:
     - User
     - YouTube title
     - YouTube link
     - Generated content (summary)
     - Date and time of creation

6. **Post Management**
   - Users can view all the posts they have created in a dedicated dashboard.
