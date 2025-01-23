from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class PDFFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='pdf/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(null=True, blank=True)
    summarized_pdf = models.FileField(upload_to='summarized_pdfs/', null=True, blank=True)
    original_language = models.CharField(max_length=10, default='en')


    def __str__(self):
        return f"{self.user.username} - {self.pdf.name}"


