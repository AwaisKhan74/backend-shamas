"""
URL configuration for shams_vision project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from core.views import DistrictViewSet, FileManagerViewSet
from finance.views import PenaltyViewSet, RewardViewSet
from leaves.views import LeaveRequestViewSet
from operations.views import StoreVisitViewSet, WorkSessionViewSet
from notifications.views import NotificationViewSet

router = DefaultRouter()
router.register('files', FileManagerViewSet, basename='files')
router.register('leaves', LeaveRequestViewSet, basename='leaves')
router.register('finance/rewards', RewardViewSet, basename='rewards')
router.register('administration/penalties', PenaltyViewSet, basename='penalties')
router.register('operations/sessions', WorkSessionViewSet, basename='work-sessions')
router.register('operations/districts', DistrictViewSet, basename='districts')
router.register('operations/store-visits', StoreVisitViewSet, basename='store-visits')
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
