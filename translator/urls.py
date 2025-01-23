# translator/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('translator/', views.translator, name='translator'),
    path('view_pdfs/', views.view_pdfs, name='view_pdfs'),
    path('translate_pdf/<int:pk>/', views.translate_pdf, name='translate_pdf'),
    path('view_translated_pdfs/', views.view_translated_pdfs, name='view_translated_pdfs'),
]
