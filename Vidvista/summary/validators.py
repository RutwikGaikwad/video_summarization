from django.core.exceptions import ValidationError

def file_type(value):
  file = value
  if file and not file.name.endswith('.mp4'):
    raise ValidationError("Please upload mp4 file")