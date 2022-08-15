from django.urls import path
from django.contrib.auth import views as auth_views
from core.patient_web import views
from django.contrib import admin

urlpatterns = [
    path('', views.sign_in, name='login_patient'),
    path('sign_up/', views.sign_up, name='sign_up_page'),
    path('main/', views.main, name='patient_main_page'),
    path('dashboard/', views.patient_dahboard, name='patient_dashboard'),
    
]