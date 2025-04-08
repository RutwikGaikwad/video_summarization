from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import youtubeURL, Video_mp4_form, UserRegistrationForm, FeedbackForm
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from .models import Video_mp4, User
from .video import summariza_text
import moviepy.editor as mp
from django.conf import settings
import os
import assemblyai as aai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
import yt_dlp
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import get_object_or_404

# Accuracy Evaluation Imports
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util

# Load Sentence Transformer Model (Optimized)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Feedback
@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            # Process the data (e.g., save to database, send email, etc.)
            # For now, just redirect to a thank-you page
            return redirect('home')  # You should create a `thank_you` URL/view
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback.html', {'form': form})

# User registeration 
def register(request):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.set_password(form.cleaned_data['password1'])
      user.save()
      login(request,user)
      return redirect('home')
  else:
    form = UserRegistrationForm()
  return render(request,'registration/register.html',{'form':form})

# Function to Evaluate Summary Accuracy
def evaluate_summary(original_text, summary_text):
    """
    Evaluates the accuracy of a summary using ROUGE-L and Cosine Similarity.
    Uses faster sentence-transformers for embedding similarity.
    """
    # Compute ROUGE-L score
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    rouge_score = scorer.score(original_text, summary_text)['rougeL'].fmeasure * 100

    # Compute Cosine Similarity with Sentence Transformers
    original_embedding = model.encode(original_text, convert_to_tensor=True)
    summary_embedding = model.encode(summary_text, convert_to_tensor=True)
    cosine_score = util.pytorch_cos_sim(original_embedding, summary_embedding).item() * 100

    # Combine scores (50% weight to each)
    final_score = (rouge_score + cosine_score) / 2
    return {
        "rouge_score": rouge_score,
        "cosine_similarity": cosine_score,
        "final_accuracy": final_score
    }


# download summary
def download_summary(request):
    summary_text = request.GET.get('summary', 'No summary available')

    # Create a response object with PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="summary.pdf"'

    # Generate PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, "Summarized Text:")

    # Handle text wrapping
    max_width = 400  # Maximum width for text (adjust as needed)
    y_position = 730
    line_height = 20  # Space between lines

    for line in summary_text.split('\n'):
        wrapped_lines = simpleSplit(line, "Helvetica", 12, max_width)
        for wrapped_line in wrapped_lines:
            pdf.drawString(100, y_position, wrapped_line)
            y_position -= line_height
            if y_position < 50:  # Start a new page if the content exceeds the page
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750

    pdf.showPage()
    pdf.save()

    return response

# Function to Summarize Text
def summarize_text(text):
    summarizer = pipeline('summarization')

    num_iters = int(len(text) / 1000)
    summarized_text = []
    for i in range(0, num_iters + 1):
        start = i * 1000
        end = (i + 1) * 1000
        out = summarizer(text[start:end], max_length=60)
        summarized_text.append(out[0]['summary_text'])

    return " ".join(summarized_text)  # Combine into a single string


# Mp4 Video Upload Function
def Video_mp4_upload(request):
    if request.method == "POST":
        form = Video_mp4_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            latest_video = Video_mp4.objects.last()

            # Full path on the server
            full_video_path = os.path.join(settings.MEDIA_ROOT, latest_video.video.name)

            # Convert video to audio
            my_clip = mp.VideoFileClip(full_video_path)
            my_clip.audio.write_audiofile("converted_audio.wav")

            # Convert audio to text
            aai.settings.api_key = "bd8a81fa6d0647a2bffdba1aa4284adc"
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe("converted_audio.wav")

            # Check if transcript is valid
            transcript_text = getattr(transcript, 'text', None)
            if not transcript_text or not isinstance(transcript_text, str) or transcript_text.strip() == "":
                return render(request, 'website/error.html', {
                    'error_message': 'Transcription failed or returned no valid text.'
                })

            # Summarize Text
            summarized_text = summariza_text(transcript.text)
            if not summarized_text or not isinstance(summarized_text, str):
                return render(request, 'website/error.html', {
                    'error_message': 'Summarization failed or returned empty.'
                })

            # Evaluate Accuracy
            accuracy_scores = evaluate_summary(transcript.text, summarized_text)

            title = os.path.splitext(os.path.basename(full_video_path))[0]

            return render(request, 'website/summarized_result.html', {
                'title':title,
                'summarized_text': summarized_text,
                'text': transcript.text,
                'accuracy_scores': accuracy_scores
            })
    else:
        form = Video_mp4_form()
    return render(request, 'website/Mp4_video.html', {'form': form})


# YouTube URL Upload Function
def Video_url_upload(request):
    if request.method == 'POST':
        form = youtubeURL(request.POST)
        if form.is_valid():
            youtube_url = form.cleaned_data['youtube_url']

            # Extract Video ID
            youtube_id = youtube_url.split('=')[1]

            # Convert Video to Text
            transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
            result = " ".join([i['text'] for i in transcript])

            # Summarize Text
            summarized_text = summariza_text(result)

            # Evaluate Accuracy
            accuracy_scores = evaluate_summary(result, summarized_text)

            title = get_youtube_title(youtube_url)

            return render(request, 'website/summarized_result.html', {
                'title': title,
                'summarized_text': summarized_text,
                'text': result,
                'accuracy_scores': accuracy_scores
            })
    else:
        form = youtubeURL()
    return render(request, 'website/Url_video.html', {'form': form})

# Title extraction
def get_youtube_title(url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', 'No Title Found')
    except Exception as e:
        return f"Error: {str(e)}"


# Home Page Function
def home(request):
    return render(request, 'website/index.html')
