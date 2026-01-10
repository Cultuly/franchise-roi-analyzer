from django.urls import path
from .views import CalculatorView, CalculateAPIView


app_name = 'analytics'

urlpatterns = [
    path('', CalculatorView.as_view(), name='calculator'),
    path('api/calculate/', CalculateAPIView.as_view(), name='calculate_api'),
]