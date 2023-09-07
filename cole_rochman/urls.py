"""cole_rochman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_swagger_view(title='Coleroch-man API')

urlpatterns = [
    path('admin/', admin.site.urls ,name='admin'),
    path('api/v1/', include('core.api.urls')),
    path('api/v1/docs/', schema_view),
    path('manager/', include('core.manager_web.urls'), name='manager'),
    path('', include('core.patient_web.urls')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

admin.site.site_header = "Cole-rochman Admin"
admin.site.site_title = "Cole-rochman Admin"
admin.site.index_title = "Welcome to Cole-rochman Admin"
