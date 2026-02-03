from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import PaymentViewSet
from users.apps import UsersConfig

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("payments/", PaymentViewSet.as_view({'get': 'list'})),
]

urlpatterns += router.urls