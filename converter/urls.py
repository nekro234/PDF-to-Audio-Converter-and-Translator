from django.urls import path, include
from . import views 

urlpatterns = [
    path('main/', views.main_page, name='main_page'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('pdfs/', views.list_pdfs, name='list_pdfs'),
    path('delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    path('admin/analytics/', views.analytics, name='analytics'),
]
