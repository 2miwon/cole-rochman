from django.urls import path
from django.contrib.auth import views as auth_views
from core.patient_web import views
from django.contrib import admin

urlpatterns = [
    path('', views.sign_in, name='login_patient'),
    path('login/', views.sign_in),
    path('logout/', auth_views.LogoutView.as_view(), name="logout_patient"),
    path('sign_up/', views.sign_up, name='sign_up_page'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/<str:picked_year>/<str:picked_month>/<str:picked_day>',views.patient_dashboard_by_day, name = 'patient_dashboard_by_day'),
    path('password-reset/',views.password_reset, name='password_reset'),
    #path('password_modify/',views.password_modify, name='password_reset_success'),
    path('change_password/',views.change_password , name = 'patient_change_password'),
    path('community/', views.post_list, name ='community_main'),
    path('community/create/', views.post, name='post_community'),
    path('community/post/detail/<str:post_id>/', views.post_detail, name='post_detail'),    
    path('community/post/detail/delete/<str:post_id>/', views.post_delete, name='post_delete'),
    path('inspection_result/', views.inspection_result, name='inspection_result'),
    path('inspection_detail/', views.inspection_detail, name='inspection_detail'),
    path('community/<str:post_id>/comments/', views.comment, name='comments'), 
    path('community/<str:post_id>/comments/post/', views.comment_post, name='comment_post'), 
    path('community/<str:post_id>/comments/<str:comment_id>/delete/', views.comment_delete, name='comment_delete'), 
    path('community/search/',views.search, name='search'),
] 
