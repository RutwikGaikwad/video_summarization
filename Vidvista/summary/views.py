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
from rouge import Rouge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.pdfgen import canvas

# Create your views here.

# download summary
def download_summary(request):
    summary_text = request.GET.get('summary', 'No summary available')

    # Create a response object with PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="summary.pdf"'

    # Generate PDF
    pdf = canvas.Canvas(response)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, "Summarized Text:")
    
    # Split text into lines for better formatting
    y_position = 730
    for line in summary_text.split('\n'):
        pdf.drawString(100, y_position, line)
        y_position -= 20

    pdf.showPage()
    pdf.save()

    return response

# summary evaluation function
def evaluate_summary(original_text, summary_text):
  # ROUGE Score Calculation
  rouge = Rouge()
  scores = rouge.get_scores(summary_text, original_text)  # Compare summary with original text
  
  rouge_1 = scores[0]['rouge-1']['f']  # ROUGE-1 F1-score (unigrams)
  rouge_2 = scores[0]['rouge-2']['f']  # ROUGE-2 F1-score (bigrams)
  rouge_l = scores[0]['rouge-l']['f']  # ROUGE-L F1-score (longest common subsequence)

  # Cosine Similarity Calculation
  vectorizer = TfidfVectorizer().fit_transform([original_text, summary_text])
  cosine_sim = cosine_similarity(vectorizer[0], vectorizer[1])[0][0]  # Compute similarity score

  # Convert to percentage
  accuracy = {
    "ROUGE-1": round(rouge_1 * 100, 2),
    "ROUGE-2": round(rouge_2 * 100, 2),
    "ROUGE-L": round(rouge_l * 100, 2),
    "Cosine Similarity": round(cosine_sim * 100, 2)
  }

  return accuracy




# summarization function
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

      # Evaluate summary accuracy
      accuracy = evaluate_summary(transcript.text, summarized_text)


      return render(request,'website/summarized_result.html',{'summarized_text':summarized_text,'text':transcript.text,'accuracy':accuracy })
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
      summarized_text = summariza_text(result)

      # Evaluate summary accuracy
      accuracy = evaluate_summary(result, summarized_text)
      
      return render(request,'website/summarized_result.html',{'summarized_text':summarized_text ,'text':result,'accuracy':accuracy})
  else:
    form = youtubeURL()
  return render(request,'website/Url_video.html',{'form':form})


# home page function
def home(request):
  return render(request,'website/index.html')