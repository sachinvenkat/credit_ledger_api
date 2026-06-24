from django.urls import path
from .views import DepositWithdrawAPIView, LoanDisbursalAPIView, LoanRepaymentAPIView

urlpatterns = [
    path('accounts/<uuid:account_id>/transaction/', DepositWithdrawAPIView.as_view(), name='account-transaction'),   
    path('loans/<uuid:loan_id>/disburse/', LoanDisbursalAPIView.as_view(), name='loan_disburse'),
    path('loans/<uuid:loan_id>/repay/', LoanRepaymentAPIView.as_view(), name='loan-repay'),
]


