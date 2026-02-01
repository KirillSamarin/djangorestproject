from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from .models import Payment
from .serializers import PaymentSerializer

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
