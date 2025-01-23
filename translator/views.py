# translator/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from converter.models import PDFFile  # Import PDFFile model
from .models import PDFDocument
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import os, io
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.conf import settings

# Ensure Pytesseract knows where the Tesseract executable is
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@login_required
def translator(request):
    return render(request, 'translator/testindex.html')

@login_required
def view_pdfs(request):
    documents = PDFFile.objects.filter(user=request.user)
    return render(request, 'translator/view_pdfs.html', {'documents': documents})

@login_required
def translate_pdf(request, pk):
    pdf_file = get_object_or_404(PDFFile, pk=pk, user=request.user)
    if request.method == 'POST':
        target_language = request.POST.get('target_language').lower()
        language_codes = {
            'ms': 'ms',
            'ta': 'ta',
            'en': 'en',
            'ar': 'ar',
            'es': 'es'  # Spanish
        }
        target_language_code = language_codes.get(target_language, None)
        if not target_language_code:
            return HttpResponse("Unsupported language code.", status=400)

        pdf_text = extract_text_from_pdf(pdf_file.pdf.path, target_language_code)
        if not pdf_text:
            return HttpResponse("No text found in the PDF.", status=400)
        
        translated_text = GoogleTranslator(source='auto', target=target_language_code).translate(pdf_text)
        pdf_path = create_pdf_with_text(translated_text, target_language_code, pdf_file)

        # Update or create the PDFDocument entry
        document, created = PDFDocument.objects.get_or_create(user=request.user, pdf_file=pdf_file)
        setattr(document, f'translated_file_{target_language_code}', pdf_path)
        document.save()

        return redirect('view_pdfs')
    return redirect('view_pdfs')

def extract_text_from_pdf(pdf_path, lang):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text += page_text
        else:
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                with Image.open(io.BytesIO(image_bytes)) as img:
                    img = img.convert('L')
                    img = img.filter(ImageFilter.MedianFilter())
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(2)
                    custom_config = r'--oem 3 --psm 6'
                    text += pytesseract.image_to_string(img, lang=lang, config=custom_config)
    return text

def create_pdf_with_text(text, lang, pdf_file):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'translated_pdfs')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'translated_{lang}_{pdf_file.id}.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Font registration and selection
    if lang == 'ta':
        pdfmetrics.registerFont(TTFont('NotoSansTamil', 'static/fonts/NotoSansTamil-Regular.ttf'))
        font_name = 'NotoSansTamil'
    elif lang == 'ar':
        pdfmetrics.registerFont(TTFont('NotoSansArabic', 'static/fonts/NotoSansArabic-Regular.ttf'))
        font_name = 'NotoSansArabic'
    else:
        pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))
        font_name = 'NotoSans'

    c.setFont(font_name, 12)
    text_object = c.beginText(40, 750)
    text_object.textLines(text)
    c.drawText(text_object)
    c.showPage()
    c.save()

    relative_path = os.path.join('translated_pdfs', f'translated_{lang}_{pdf_file.id}.pdf')
    return relative_path


@login_required
def view_translated_pdfs(request):
    documents = PDFDocument.objects.filter(user=request.user)
    return render(request, 'translator/view_translated_pdfs.html', {'documents': documents})