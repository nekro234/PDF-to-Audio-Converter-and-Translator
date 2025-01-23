from django import forms
from .models import PDFFile

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ['pdf']
