from django.db import models
from .validators import file_type
from django.contrib.auth.models import User

# Create your models here.
class Video_mp4(models.Model):
  video = models.FileField(upload_to="video/%y",validators=[file_type])
  
class FeedBack(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  rating_choices = [
    ('5', 'Excellent'),
    ('4', 'Very Good'),
    ('3', 'Good'),
    ('2', 'Fair'),
    ('1', 'Poor'),
  ]
  rating = models.CharField(max_length=1,choices=rating_choices)
  comments = models.TextField(max_length=500)
  created_at = models.DateTimeField(auto_now_add=True)
  modified_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.user.username} - {self.comments[:20]}'