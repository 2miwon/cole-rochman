from django.urls import path
from django.contrib.auth import views as auth_views
from core.patient_web import views
from django.contrib import admin

urlpatterns = [
    path('', views.sign_in, name='login_patient'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout_patient"),
    path('sign_up/', views.sign_up, name='sign_up_page'),
    path('main/', views.main, name='patient_main_page'),
    path('dashboard/', views.patient_dahboard, name='patient_dashboard'),
    path('password-reset/',views.password_reset, name='password_reset'),
    path('change_password/',views.change_password , name = 'patient_change_password'),
    path('community/', views.post_list, name ='community_main'),
    path('community/create/', views.post, name='post_community'),
    path('community/detail/<str:post_id>', views.post_detail, name='post_detail'),    
] 