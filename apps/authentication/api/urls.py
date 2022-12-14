from apps.authentication.api import views
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('user', views.get_auth_user, name='get_auth_user'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('referral-code', views.create_referral_code, name='create_referral_code'),
    path('', include(router.urls)),
]
