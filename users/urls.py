from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import PaymentViewSet, UserCreateAPIView
from users.apps import UsersConfig
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('payments/', PaymentViewSet.as_view({'get': 'list'}), name='payments_get'),
]

urlpatterns += router.urls