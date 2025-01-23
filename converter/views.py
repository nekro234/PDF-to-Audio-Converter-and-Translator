from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PDFUploadForm
from .models import PDFFile
import os
from gtts import gTTS
from PyPDF2 import PdfReader
import pyttsx3
from django.conf import settings


# Create your views here.
@login_required
def main_page(request):
    return render(request, "converter/main.html", {'fname': request.user.first_name})


def upload_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf']
            PDFFile.objects.create(user=request.user, pdf=pdf_file)
            pdf_file.original_language = request.POST.get('original_language', 'en')
            return redirect('list_pdfs')
    else:
        form = PDFUploadForm()
    return render(request, "converter/upload_pdf.html", {'form': form})


def list_pdfs(request):
    # Fetch PDFs uploaded by the logged-in user
    user_pdfs = PDFFile.objects.filter(user=request.user)
    return render(request, 'converter/list_pdfs.html', {'pdfs': user_pdfs})


def delete_pdf(request, pdf_id):
    pdf = get_object_or_404(PDFFile, id=pdf_id, user=request.user)
    if request.method == "POST":
        pdf.delete()
        return redirect('list_pdfs')
    return render(request, 'converter/delete_pdf.html', {'pdf': pdf})


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from converter.models import PDFFile
from translator.models import PDFDocument

@staff_member_required
def analytics(request):
    total_users = User.objects.count()
    total_pdfs = PDFFile.objects.count()
    total_translated_pdfs = PDFDocument.objects.exclude(translated_file_en__isnull=True).count()
    total_summarized_pdfs = PDFFile.objects.exclude(summarized_pdf__isnull=True).count()

    context = {
        'total_users': total_users,
        'total_pdfs': total_pdfs,
        'total_translated_pdfs': total_translated_pdfs,
        'total_summarized_pdfs': total_summarized_pdfs,
    }

    return render(request, 'converter/analytics.html', context)