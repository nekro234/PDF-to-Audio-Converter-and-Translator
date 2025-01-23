from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary, name='summary'),
    path('save_summary_as_pdf/', views.save_summary_as_pdf, name='save_summary_as_pdf'),
     path('list_summarized_pdfs/', views.list_summarized_pdfs, name='list_summarized_pdfs'),
]
