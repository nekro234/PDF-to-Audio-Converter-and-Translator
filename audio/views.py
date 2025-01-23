from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Voice, AudioFile
from converter.models import PDFFile
from gtts import gTTS, gTTSError
from django.conf import settings
import pytesseract
import os, io
import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageEnhance
from pydub import AudioSegment
from pydub.playback import play

# Ensure Pytesseract knows where the Tesseract executable is
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@login_required
def select_pdf(request):
    pdfs = PDFFile.objects.filter(user=request.user)
    return render(request, 'audio/select_pdf.html', {'pdfs': pdfs})

@login_required
def list_voices(request, pdf_id):
    pdf_file = get_object_or_404(PDFFile, id=pdf_id, user=request.user)
    voices = Voice.objects.all()
    return render(request, 'audio/list_voices.html', {'voices': voices, 'pdf_file': pdf_file})

@login_required
def convert_pdf_to_audio(request, pdf_id):
    pdf_file = get_object_or_404(PDFFile, id=pdf_id, user=request.user)
    if request.method == "POST":
        voice_id = request.POST.get('voice_id')
        voice = get_object_or_404(Voice, id=voice_id)
        
        # Extract text from PDF
        pdf_path = pdf_file.summarized_pdf.path if pdf_file.summarized_pdf else pdf_file.pdf.path
        pdf_text = extract_text_from_pdf(pdf_path, voice.language)
        
        # Convert text to audio
        tts = gTTS(text=pdf_text, lang=voice.language, slow=False)
        audio_filename = f"{pdf_file.id}_{voice.language}_{voice.gender}.mp3"
        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', audio_filename)
        
        # Ensure the directory exists
        audio_dir = os.path.dirname(audio_path)
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        try:
            tts.save(audio_path)
        except gTTSError as e:
            # Handle the error gracefully, maybe log the error and show a user-friendly message
            print(f"Error converting text to audio: {e}")
            return render(request, 'audio/error.html', {'message': 'Failed to convert PDF to audio. Please try again later.'})
        
        # Save the audio file record
        AudioFile.objects.create(user=request.user, pdf_file=pdf_file, audio=f'audio_files/{audio_filename}')
        
        return redirect('list_audios')

    voices = Voice.objects.filter(language=pdf_file.original_language)  # Adjust this if you have language detection
    return render(request, 'audio/convert_pdf_to_audio.html', {'pdf_file': pdf_file, 'voices': voices})

@login_required
def list_audios(request):
    audio_files = AudioFile.objects.filter(user=request.user)
    return render(request, 'audio/list_audios.html', {'audio_files': audio_files})

def extract_text_from_pdf(pdf_path, lang):
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    import io

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
        if not text.strip():  # If text extraction fails, try OCR
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                text += pytesseract.image_to_string(image, lang=lang)
    return text

@login_required
def mood_based_reader(request):
    if request.method == 'POST':
        audio_id = request.POST.get('audio_id')
        mood = request.POST.get('mood')
        audio_file = get_object_or_404(AudioFile, id=audio_id, user=request.user)
        
        audio_path = audio_file.audio.path
        sound = AudioSegment.from_file(audio_path)

        if mood == 'happy':
            sound = sound.speedup(playback_speed=2.0)
        elif mood == 'sad':
            sound = sound.speedup(playback_speed=1.4)
        elif mood == 'angry':
            sound = sound + 40  # Increase volume

        output_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', f'{audio_file.id}_{mood}.mp3')
        sound.export(output_path, format='mp3')
        
        return redirect('list_audios')

    audio_files = AudioFile.objects.filter(user=request.user)
    return render(request, 'audio/mood_based_reader.html', {'audio_files': audio_files})