"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from App.common.views import (
    export_admission_inquiries_view,
    export_guest_feedback_view,
    export_service_inquiries_view,
)

urlpatterns = [
    # Export endpoints for Excel (.xlsx) and CSV
    path('admin/export/service-inquiries/<str:format>/', export_service_inquiries_view, name='export-service-inquiries'),
    path('admin/export/admission-inquiries/<str:format>/', export_admission_inquiries_view, name='export-admission-inquiries'),
    path('admin/export/guest-submissions/<str:format>/', export_guest_feedback_view, name='export-guest-submissions'),

    path('admin/', admin.site.urls),
    path('api/services/', include('App.Services.urls')),
    path('api/feedback/', include('App.Feedback.urls')),
    path('api/contact/', include('App.Contact.urls')),
    path('api/ui/', include('App.UI.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()

