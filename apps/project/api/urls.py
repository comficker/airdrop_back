from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'tokens', views.TokenViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'properties', views.PropertyViewSet)
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('events/<slug:pk>/join', views.event_join),
    path('events/<slug:pk>/follow', views.event_follow)
]
