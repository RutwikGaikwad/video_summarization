from django.shortcuts import render
from django.http import HttpResponse
from .forms import youtubeURL, Video_mp4_form
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from .models import Video_mp4
from .video import summariza_text
import moviepy.editor as mp
from django.conf import settings
import os
import speech_recognition as sr
import assemblyai as aai


# Create your views here.



def summarize_text(text):
  summarizer = pipeline('summarization')
  
  num_iters = int(len(text)/1000)
  summarized_text = []
  for i in range(0,num_iters+1):
    start = 0
    start = i * 1000
    end = (i+1) * 1000
    out = summarizer(text[start:end],max_length=60)
    out = out[0]
    out = out['summary_text']
    summarized_text.append(out)
  
  return summarized_text


# Mp4 video function
def Video_mp4_upload(request):
  if request.method == "POST":
    form = Video_mp4_form(data=request.POST,files=request.FILES)
    if form.is_valid:
      form.save()
      latest_video = Video_mp4.objects.last()

      # Full path on the server
      full_video_path = os.path.join(settings.MEDIA_ROOT, latest_video.video.name)

      # URL accessible path
      video_url = latest_video.video.url

      # converting video to audio
      my_clip = mp.VideoFileClip(full_video_path)
      my_clip.audio.write_audiofile(r"converted_audio.wav")

      # converting audio to text
      aai.settings.api_key = "bd8a81fa6d0647a2bffdba1aa4284adc"
      transcriber = aai.Transcriber()
      transcript = transcriber.transcribe("converted_audio.wav")

      # calling summarization function
      summarized_text = summariza_text(transcript.text)

      return render(request,'website/summarized_result.html',{'summarized_text':summarized_text,'text':transcript.text })
  else:
    form = Video_mp4_form()
  return render(request,'website/Mp4_video.html',{'form':form})


# YouTube url function
def Video_url_upload(request):
  if request.method == 'POST':
    form = youtubeURL(request.POST)
    if form.is_valid():
      youtube_url = form.cleaned_data['youtube_url']

      # video to text conversion
      youtube_id = youtube_url.split('=')[1]

      YouTubeTranscriptApi.get_transcript(youtube_id)
      transcript = YouTubeTranscriptApi.get_transcript(youtube_id)

      result = ""
      for i in transcript:
        result += ' ' + i['text']

      # calling summarization function
      # summarized_text = summarize_text(result)

      summarize_text = summariza_text(result)

      
      return render(request,'website/summarized_result.html',{'summarized_text':summarize_text ,'text':result})
  else:
    form = youtubeURL()
  return render(request,'website/Url_video.html',{'form':form})


# home page function
def home(request):
  return render(request,'website/index.html')