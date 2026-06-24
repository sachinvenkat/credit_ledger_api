from multiprocessing import process
from django.shortcuts import render
from decimal import Decimal, InvalidOperation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from .serializers import AccountSerializer, LoanSearilizer, RepaymentSerializer
from .services import process_ledger_entry, approve_and_disburse_loan, process_loan_repayment

class DepositWithdrawAPIView(APIView):

    def post(self, request, account_id):
        # 1. Safely extrace data from request body
        amount_raw = request.data.get('amount')
        txn_type =  request.data.get('transaction_type')

        # 2. Input Validation ( Guard Clauses)
        if not amount_raw or not txn_type:
            return Response(
                {"error": "Both 'amount' and 'transaction_type' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if txn_type not in ['CREDIT', 'DEBIT']:
            return Response(
                {"error":"Invalid transaction_type. Must be 'CREDIT' or 'DEBIT'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount_raw))
            if amount <=0:
                return Response(
                    {"error":"Amount must be a postive number greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except(ValueError, InvalidOperation):
            return Response(
                {"error":"Invalid numerical format for amount."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Core Business Execution and Exception Handling
        try:
            txn = process_ledger_entry(account_id, amount, txn_type)
            return Response(
                {
                    "message":f"Successfully processed {txn_type}",
                    "transaction_id": str(txn.id),
                    "new_balance": str(txn.account.balance)
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            # Handles our "Insufficient funds" exception safely
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            # Catch-all for unexpected database failures
            return Response(
                {"error":"Internal server error processing ledger."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoanDisbursalAPIView(APIView):
    def post(self, request, loan_id):
        try:

            loan = approve_and_disburse_loan(loan_id)

            serializer = LoanSearilizer(loan)
            return Response(
                {
                    "message": "Loan successfully apporved and disbursed",
                    "loan_details": serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except ValueError as e:
            #
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST 
            )
        except Loan.DoesNotExist:
            return Response (
                {"error": "Loan not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"error", "Internal serve error during disbursal."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
class LoanRepaymentAPIView(APIView):

    def post(self, request, loan_id):
        
        serializer = RepaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_amount = serializer.validated_data['payment_amount']

        try:

            loan = process_loan_repayment(loan_id, payment_amount)

            response_serializer =  LoanSearilizer(loan)

            return Response(
                {
                    "message": "Repayment successfully processed.",
                    "loan_details": response_serializer.data
                 }
            )
        except ValueError:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Loan.DoesNotExist:
            return Response({"error": "loan not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                {"error":"Internal server error during repayment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )






        