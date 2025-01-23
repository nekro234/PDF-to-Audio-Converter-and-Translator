from django.db import models
from django.contrib.auth.models import User
from converter.models import PDFFile

class Voice(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('ms', 'Malay'),
        ('ar', 'Arabic'),
        ('es', 'Spanish'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.get_language_display()} - {self.get_gender_display()}"


class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_file = models.ForeignKey(PDFFile, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='audio_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.pdf_file.pdf.name}"
