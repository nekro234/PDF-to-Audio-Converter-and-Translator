from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('Signup', views.Signup, name="Signup"),
    path('signin', views.signin, name="signin"),
    path('Signout', views.Signout, name="Signout"),
    path('manage_profile/', views.manage_profile, name='manage_profile'),
]
