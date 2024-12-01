from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from django.core.validators import validate_email
from django.conf import settings
from random import randint

from manager.serializers import ApprovalRequestSerializer
from manager.models import WriteApprovalRequest
from .serializers import RegisterSerializer, LoginSerializer
from .models import UserModel, AccountVerificationOTP


# Function to send email for verification
def sendMailWithOTP(user, purpose):
    otp = randint(100000, 999999) # Generates a random 6 digit number for OTP
    AccountVerificationOTP.objects.create(user=user, otp=str(otp))

    # Email content
    subject = "OTP From Articles Application"
    message = render_to_string(
        'verificationMail.html',{
            'name': user.first_name,
            'uid': user.uid,
            'otp': str(otp),
            'purpose': purpose
        })
    recipient_list = [user.email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


class RegisterView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = RegisterSerializer(data=data)

            if not serializer.is_valid():
                return Response({
                    "success": False,
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the email already exists
            if UserModel.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({
                    "success": False,
                    "error": "Account already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.is_active = False
            user.save()

            sendMailWithOTP(user, "verify your account") # Sends email with OTP for verification

            return Response({
                "success": True,
                "message": "Account created successfully. Please verify your email.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as ex:
            print(ex)
            return Response({
                "success": False,
                "error": "Something went wrong. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            uid = request.data.get('uid')
            otp = request.data.get('otp')

            if not uid or not otp:
                return Response({
                    "success": False,
                    "error": "UID and OTP are required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(UserModel, uid=uid)
            otp_obj = AccountVerificationOTP.objects.filter(user=user).order_by('-created_at').first()

            # Check if the account is already activated
            if user.is_active:
                return Response({
                    "success": True,
                    "error": "Your account has been already verified and activated."
                },status=status.HTTP_200_OK)

            # Check if UID is valid or OTP is expired
            if not otp_obj or not otp_obj.is_valid():
                return Response({
                    "success": False,
                    "error": "The OTP has expired. Please request for another one."
                },status=status.HTTP_400_BAD_REQUEST)

            # OTP Verification
            if otp == otp_obj.otp:
                user.is_active = True # Activates user account
                user.save()

                otp_obj.is_used = True # Marks OTP as used
                otp_obj.save()

                return Response({
                    "success": True,
                    "message": "Account activated successfully."
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "error": "Invalid OTP. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST) 

        except Exception as ex:
            return Response({
                "success": False,
                "message": "Something went wrong. Please try again.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendMailWithOTPView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email', '').strip()
            if not email:
                raise ValidationError("Please provide your registered email address for verification.")
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Please provide a valid email address.")
            
            user = get_object_or_404(UserModel, email=email)            
            sendMailWithOTP(user, "reset your account password along with New Password") # Sends email with OTP for verification

            return Response({
                "success": True,
                "message": "OTP is sent to your registered email. Kindly verify."
            }, status=status.HTTP_200_OK)
        
        except ValidationError as ve:
            return Response({
                "success": False,
                "error": str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as ex:
            return Response({
                "success": False,
                "error": "Something went wrong. Please try again.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                response = serializer.get_jwt_token(serializer.validated_data)
                return Response(response, status=status.HTTP_200_OK)
            
            return Response({
                "success" : False,
                "message" : "Error occured. Check details",
                "error" : serializer.errors
            }, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as ex:
            print(ex)
            return Response({
                "success" : False,
                "message" : "Something went wrong. Please try again.",
            }, status = status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            uid = request.data.get('uid')
            otp = request.data.get('otp')
            new_password = request.data.get('new_password')
            print(uid, otp, new_password)

            if not uid or not otp or not new_password:
                return Response({
                    "success": False,
                    "error": "uid, otp and new_password fields are required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(UserModel, uid=uid)
            otp_obj = AccountVerificationOTP.objects.filter(user=user).order_by('-created_at').first()

            if not otp_obj or not otp_obj.is_valid():
                return Response({
                    "success": False,
                    "error": "The UID id invalid or the OTP has expired."
                },status=status.HTTP_400_BAD_REQUEST)

            # OTP Verification
            if otp == otp_obj.otp:
                user.set_password(new_password)
                user.save()

                otp_obj.is_used = True # Marks OTP as used
                otp_obj.save()

                subject = "Password Reset Successfully."
                message = render_to_string(
                    'confirmationMail.html',
                    {
                        'name': user.first_name,
                        'uid': user.uid,
                        'password': new_password
                    },
                )
                recipient_list = [user.email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

                return Response({
                    "success": True,
                    "message": "Password reset successfully."
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "error": "Invalid OTP. Kindly try again."
            }, status=status.HTTP_400_BAD_REQUEST) 

        except Exception as ex:
            return Response({
                "success": False,
                "message": "Something went wrong. Please try again.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SubmitApprovalRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:            
            serializer = ApprovalRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            message = request.data.get('message')
            WriteApprovalRequest.objects.create(user=request.user, message=message)

            return Response({
                "status": True,
                "message": "Request submitted successfully. Our team will update you soon."
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as ex:
            return Response({
                "success": False,
                "error": str(ex)
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                "success": False,
                "error": "An error occurred while processing your request. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
