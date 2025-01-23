import os
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import fitz  # PyMuPDF
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from converter.models import PDFFile

# Initialize the multilingual summarizer
model_name = "facebook/mbart-large-50"
model = MBartForConditionalGeneration.from_pretrained(model_name)
tokenizer = MBart50TokenizerFast.from_pretrained(model_name)

@login_required
def summary(request):
    if request.method == 'POST':
        pdf_id = request.POST.get('pdf_id')
        change_type = request.POST.get('change_type')
        pdf_file = get_object_or_404(PDFFile, id=pdf_id, user=request.user)
        pdf_path = pdf_file.pdf.path

        # Extract text from PDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()

        # Summarize text in chunks
        if change_type == 'small':
            max_length = 300
            min_length = 100
        else:
            max_length = 150
            min_length = 50
        
        summarizer_ans = summarize_text(text, max_length, min_length, pdf_file.original_language)

        # Save summary to the model
        pdf_file.summary = summarizer_ans
        pdf_file.save()

        # Save summarized text as a new PDF
        summarized_pdf_path = save_summary_as_pdf(pdf_file, summarizer_ans, pdf_file.original_language)
        pdf_file.summarized_pdf = summarized_pdf_path
        pdf_file.save()

        return render(request, 'summarizer/view_summary.html', {'pdf_file': pdf_file})

    pdfs = PDFFile.objects.filter(user=request.user)
    return render(request, 'summarizer/summarizer.html', {'pdfs': pdfs})

def summarize_text(text, max_length, min_length, language):
    # Map the language to the mBART model language code
    language_map = {
        'ta': 'ta_IN',  # Tamil
        'ar': 'ar_AR',  # Arabic
        'es': 'es_XX',  # Spanish
        'ms': 'ms_MY',  # Malay
        'en': 'en_XX',  # English (default)
    }
    language_code = language_map.get(language, 'en_XX')
    tokenizer.src_lang = language_code
    tokenizer.tgt_lang = language_code

    # Split the text into chunks that fit the model's input limits
    max_chunk_length = 1024
    chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    summarized_chunks = []
    
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs["input_ids"], max_length=max_length, min_length=min_length, num_beams=4, forced_bos_token_id=tokenizer.lang_code_to_id[language_code])
        summarized_chunk = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        summarized_chunks.append(summarized_chunk)
    
    return ' '.join(summarized_chunks)

def save_summary_as_pdf(pdf_file, summary_text, language):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 1 * inch
    text_width = width - 2 * margin

    # Register fonts for different languages
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    if language == 'ta':
        pdfmetrics.registerFont(TTFont('NotoSansTamil', os.path.join(font_dir, 'NotoSansTamil-Regular.ttf')))
        font_name = 'NotoSansTamil'
    elif language == 'ar':
        pdfmetrics.registerFont(TTFont('NotoSansArabic', os.path.join(font_dir, 'NotoSansArabic-Regular.ttf')))
        font_name = 'NotoSansArabic'
    else:
        pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(font_dir, 'NotoSans-Regular.ttf')))
        font_name = 'NotoSans'

    c.setFont(font_name, 12)
    c.drawString(margin, height - margin, "Summary of " + pdf_file.pdf.name)

    text_object = c.beginText(margin, height - 2 * margin)
    text_object.setFont(font_name, 12)

    # Split the summary text into lines that fit the text width
    lines = summary_text.split('\n')
    for line in lines:
        wrapped_lines = wrap_text(line, text_width, c)
        for wrapped_line in wrapped_lines:
            if text_object.getY() < margin:
                c.drawText(text_object)
                c.showPage()
                text_object = c.beginText(margin, height - margin)
                text_object.setFont(font_name, 12)
            text_object.textLine(wrapped_line)

    c.drawText(text_object)
    c.showPage()
    c.save()

    buffer.seek(0)

    # Ensure the directory exists
    summarized_pdf_dir = os.path.join(settings.MEDIA_ROOT, 'summarized_pdfs')
    if not os.path.exists(summarized_pdf_dir):
        os.makedirs(summarized_pdf_dir)

    summarized_pdf_path = os.path.join(summarized_pdf_dir, f'summarized_{pdf_file.id}.pdf')
    with open(summarized_pdf_path, 'wb') as f:
        f.write(buffer.getvalue())

    return summarized_pdf_path


def wrap_text(text, width, canvas):
    lines = []
    while text:
        if canvas.stringWidth(text) <= width:
            lines.append(text)
            break
        else:
            for i in range(len(text)):
                if canvas.stringWidth(text[:i]) > width:
                    lines.append(text[:i-1])
                    text = text[i-1:]
                    break
    return lines

@login_required
def list_summarized_pdfs(request):
    try:
        pdfs = PDFFile.objects.filter(user=request.user, summarized_pdf__isnull=False)
    except PDFFile.DoesNotExist:
        pdfs = []
    
    # Check if summarized_pdf URLs are accessible
    accessible_pdfs = []
    for pdf in pdfs:
        if pdf.summarized_pdf and os.path.exists(pdf.summarized_pdf.path):
            accessible_pdfs.append(pdf)
    
    return render(request, 'summarizer/list_summarized_pdfs.html', {'pdfs': accessible_pdfs})
