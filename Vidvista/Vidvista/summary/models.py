from django.db import models
from .validators import file_type

# Create your models here.
class Video_mp4(models.Model):
  video = models.FileField(upload_to="video/%y",validators=[file_type])
  