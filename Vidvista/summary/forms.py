from django import forms
from .models import Video_mp4

class youtubeURL(forms.Form):
  youtube_url = forms.URLField(widget=forms.URLInput(attrs={
    'placeholder':'Enter youtube URL here',
    'class': 'form-control'
  }))

class Video_mp4_form(forms.ModelForm):
  class Meta:
    model = Video_mp4
    fields=('video',)