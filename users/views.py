from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from .models import Payment, User
from .serializers import UserSerializer
from .serializers import PaymentSerializer

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Получение списка платежей",
    tags=['Payments'],
    manual_parameters=[
        openapi.Parameter(
            'paid_course',
            openapi.IN_QUERY,
            description="Фильтр по ID курса",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'paid_lesson',
            openapi.IN_QUERY,
            description="Фильтр по ID урока",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'payment_method',
            openapi.IN_QUERY,
            description="Фильтр по методу оплаты (cash или transfer)",
            type=openapi.TYPE_STRING,
            enum=['cash', 'transfer']
        ),
        openapi.Parameter(
            'ordering',
            openapi.IN_QUERY,
            description="Сортировка по payment_date (добавьте - для обратной сортировки)",
            type=openapi.TYPE_STRING
        ),
    ]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Получение информации о платеже",
    tags=['Payments']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Создание нового платежа",
    tags=['Payments']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Обновление платежа",
    tags=['Payments']
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Частичное обновление платежа",
    tags=['Payments']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Удаление платежа",
    tags=['Payments']
))
class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']

class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
