import shutil
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
import os
import assemblyai as aai
import yt_dlp
import openai
from .models import BlogPost


# Create your views here.


@login_required # just how is logged in can access this page
def index(request):
    return render(request, 'index.html')

## Functions for handling login logout and signin
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
            # Delete the entire media folder
            media_folder_path = os.path.join(settings.BASE_DIR, "media")
            if os.path.exists(media_folder_path):
                shutil.rmtree(media_folder_path)  # Deletes the folder and all its contents
                print(f"Media folder deleted: {media_folder_path}")
            else:
                print(f"Media folder not found: {media_folder_path}")
            return JsonResponse({'error': 'Faild to get transcript'}, status=500)
        
        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(yt_transcript)
        if not blog_content:
            return JsonResponse({'error':'Faild to generate blg article'}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
                user = request.user,
                youtube_title = yt_title,
                youtube_link = yt_link,
                generated_content = blog_content,
        )
        new_blog_article.save()


            # Delete the entire media folder
        media_folder_path = os.path.join(settings.BASE_DIR, "media")
        if os.path.exists(media_folder_path):
            shutil.rmtree(media_folder_path)  # Deletes the folder and all its contents
            print(f"Media folder deleted: {media_folder_path}")
        else:
            print(f"Media folder not found: {media_folder_path}")

        # return blog aricle as response
        return JsonResponse({'content':blog_content})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

## Functions needed for the generate_blog
def get_yt_title(link):
    try:
        ydl_opts = {
            'quiet': True,  # Suppresses verbose output
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)  # Extract video info without downloading
            return info.get('title', 'Title unavailable')  # Safely fetch the title
    except yt_dlp.utils.DownloadError as e:
        return f"Error fetching title: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

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

    # limitate lenght of the trascription dude the limitation of the free GooseAI model Fairseq 1.3B at 2048
    def limit_transcription_size(text, max_tokens):
        words = text.split()  # Split by words (approximation of tokens)
        if len(words) > max_tokens:
            return " ".join(words[:max_tokens])  # Trim to max_tokens words
        return text

    transcription = limit_transcription_size(transcription, 1500)
    
    openai.api_base = "https://api.goose.ai/v1"
    openai.api_key = os.environ.get("GOOSEAI_KEY")

    # Create the blog post prompt
    prompt = (
    f"Summarize the following text:\n\n{transcription}\n\nSummary:"
)

    # Generate completion using the fairseq-1.3b engine
    try:
        completion = openai.Completion.create(
            engine="gpt-j-6b",
            prompt= prompt,
            max_tokens=200,
            stream=False
        )

        # Extract and return the generated content
        generated_content = completion.choices[0].text.strip()
        return generated_content

    except openai.error.OpenAIError as e:
        print(f"Error generating blog: {e}")
        return None


## Function to see all generated posts
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request,'pages/all-blogs.html', {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'pages/blog-details.html', {'blog_article_detail' : blog_article_detail})
    else:
        return redirect('/')


