from django.urls import path
from . import views

urlpatterns = [
    path('voices/<int:pdf_id>/', views.list_voices, name='list_voices'),
    path('convert/<int:pdf_id>/', views.convert_pdf_to_audio, name='convert_pdf_to_audio'),
    path('audios/', views.list_audios, name='list_audios'),
    path('select_pdf/', views.select_pdf, name='select_pdf'),
    path('audio/mood_based_reader/', views.mood_based_reader, name='mood_based_reader'),
]
