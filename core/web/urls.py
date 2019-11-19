from django.urls import path
from core.web import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('menu', views.web_menu, name='web_menu'),
    path('dashboard', views.user_dashboard, name='user_dashboard'),
    path('dashboard/<int:pid>', views.patient_status, name='patient_status'),
    path('login', views.sign_in, name='login_user'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout", ),

]
