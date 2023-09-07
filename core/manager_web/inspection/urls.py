from django.urls import path
from core.manager_web import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inspection, name='inspection'),
    # path('dashboard/inspection/<int:pid>/create/', views.patient_inspection_create, name='patient_inspection_create'),
    path('<int:pid>/', views.patient_inspection, name='patient_inspection'),
    path('update/<int:pid>/<int:sputum_id>/', views.patient_inspection_update, name='patient_inspection_update'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout", ),
]
