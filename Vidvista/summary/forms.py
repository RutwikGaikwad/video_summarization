from django import forms
from .models import Video_mp4,FeedBack
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class youtubeURL(forms.Form):
  youtube_url = forms.URLField(widget=forms.URLInput(attrs={
    'placeholder':'Enter youtube URL here',
    'class': 'form-control'
  }))

class Video_mp4_form(forms.ModelForm):
  class Meta:
    model = Video_mp4
    fields=('video',)

class UserRegistrationForm(UserCreationForm):
  email = forms.EmailField()
  class Meta:
    model = User
    fields = ('username','email','password1','password2')

class FeedbackForm(forms.ModelForm):
    class Meta:
      model = FeedBack
      fields = ('rating','comments')