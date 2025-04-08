from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
  path('',views.home,name='home'),
  path('url/',views.Video_url_upload,name='video_url'),
  path('mp4/',views.Video_mp4_upload,name='video_mp4'),
  path('download_summary/',views.download_summary,name='download_summary')
]
