from django.urls import path
from .views import DepositWithdrawAPIView

urlpatterns = [
    path('accounts/<uuid:account_id>/transaction/', DepositWithdrawAPIView.as_view(), name='account-transaction'),   
]


