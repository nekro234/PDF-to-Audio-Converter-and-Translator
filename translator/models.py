# translator/models.py

from django.contrib.auth.models import User
from django.db import models
from converter.models import PDFFile  # Import PDFFile model

class PDFDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_file = models.ForeignKey(PDFFile, on_delete=models.CASCADE)  # Reference to PDFFile
    translated_file_ms = models.FileField(upload_to='translated_pdfs/', null=True, blank=True)
    translated_file_ta = models.FileField(upload_to='translated_pdfs/', null=True, blank=True)
    translated_file_en = models.FileField(upload_to='translated_pdfs/', null=True, blank=True)
    translated_file_ar = models.FileField(upload_to='translated_pdfs/', null=True, blank=True)
    translated_file_es = models.FileField(upload_to='translated_pdfs/', null=True, blank=True)
