from django.urls import path
from core.manager_web import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('menu/', views.web_menu, name='web_menu'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/<int:pid>/', views.patient_status, name='patient_status'),
    path('dashboard/inspection/', views.inspection, name='inspection'),
    path('dashboard/inspection/<int:pid>', views.patient_inspection, name='patient_inspection'),
    path('login/', views.sign_in, name='login_user'),
    path('', views.sign_in, name='index'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout", ),
]
