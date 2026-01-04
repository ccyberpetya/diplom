# netology_pd_diplom/urls.py
"""netology_pd_diplom URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from backend.views import admin_import_view, social_auth, SentryTestView, AvatarUploadView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls', namespace='backend')),
    path('admin/import/', admin_import_view, name='admin-import'),

    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Социальная авторизация
    path('auth/', include('social_django.urls', namespace='social')),

    # Новые endpoints
    path('api/v1/sentry-test/', SentryTestView.as_view(), name='sentry-test'),
    path('api/v1/user/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
]

# Статические и медиа файлы в development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)