from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
from pytube.exceptions import PytubeError
import os
import assemblyai as aai
import yt_dlp
import openai


# Create your views here.
@login_required # just how is logged in can access this page
def index(request):
    return render(request, 'index.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid Username or Password'
            return render(request, 'pages/login.html', {'error_message': error_message})


    return render(request, 'pages/login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error create account' # I can also check why the error, like the username or email is already taken
                return render(request, 'signup.html', {'error_message': error_message})

        else:
            error_message = 'Password do not match'
            return render(request, 'pages/signup.html', {'error_message': error_message})

    return render(request, 'pages/signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        yt_title = get_yt_title(yt_link)
            
        # get transcript
        yt_transcript = get_yt_transcript(yt_link)
        if not yt_transcript:
            return JsonResponse({'error': 'Faild to get transcript'}, status=500)
        
        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(yt_transcript)
        if not blog_content:
            return JsonResponse({'error':'Faild to generate blg article'}, status=500)

        # save blog article to database

        # return blog aricle sa response
        return JsonResponse({'content':blog_content})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    


def get_yt_title(link):
    try:
        yt = YouTube(link)
        return yt.title
    except KeyError:
        return "Title unavailable"
    except PytubeError as e:
        return f"Error fetching title: {e}"

def get_yt_transcript(link):
    audio_file = download_audio(link)
    aai.settings.api_key = os.environ.get('AAI_KEY')
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'media/%(title)s.mp3',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        return ydl.prepare_filename(info_dict)


def generate_blog_from_transcription(transcription): 
    openai.api_base = "https://api.goose.ai/v1"
    openai.api_key = os.environ.get("GOOSEAI_KEY")

    # Create the blog post prompt
    prompt = (
        f"Based on the following transcript from a YouTube video, write a comprehensive blog article. "
        f"Make it look like a proper blog article rather than a transcript:\n\n{transcription}\n\nBlog Article:"
    )

    # Generate completion using the fairseq-1.3b engine
    try:
        completion = openai.Completion.create(
            engine="fairseq-1-3b",  # Use the Fairseq 1.3B engine
            prompt=prompt,
            max_tokens=500,        # Adjust the token limit as needed
            temperature=0.7,       # Controls randomness (higher = more creative, lower = more focused)
            top_p=0.9,             # Nucleus sampling
            stream=False           # Disable streaming for simplicity
        )

        # Extract and return the generated content
        generated_content = completion.choices[0].text.strip()
        return generated_content

    except openai.error.OpenAIError as e:
        print(f"Error generating blog: {e}")
        return None

    





