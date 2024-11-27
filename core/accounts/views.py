from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import PermissionDenied

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from django.conf import settings
from random import randint

from .models import UserModel, AccountVerificationOTP 
from .serializers import *
from .permissions import IsAdmin


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

            otp = randint(100000, 999999) # Generates a random 6 digit number for OTP
            AccountVerificationOTP.objects.create(user=user, otp=str(otp))

            # Sending email
            subject = "OTP To Activate Articles App Account"
            message = render_to_string(
                'verificationMail.html',
                {
                    'name': user.first_name,
                    'password': data.get('password'),
                    'uid': user.uid,
                    'otp': str(otp),
                },
            )
            recipient_list = [user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

            return Response({
                "success": True,
                "message": "Account created successfully. Please verify your email."
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

            if not otp_obj or not otp_obj.is_valid():
                return Response({
                    "success": False,
                    "error": "The OTP is invalid or has expired."
                },status=status.HTTP_400_BAD_REQUEST)

            # Verifying the OTP
            if otp == otp_obj.otp:
                user.is_active = True # Activates user account
                user.save()

                otp_obj.used = True # Marks OTP as used
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
            print(ex)
            return Response({
                "success": False,
                "error": "Something went wrong. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
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


class CreateAdminOrModeratorView(APIView):
    permission_classes = [IsAdmin]  # Only Admins can access this view

    def post(self, request):
        try:
            data = request.data
            role = data.get('role')

            serializer = RoleCreateSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    "success" : False,
                    "message": "Invalid data.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has admin permissions to create other admins or moderators
            if request.user.role != 'admin':
                raise PermissionDenied("You are not authorized to create admins or moderators.")
            
            # Validate the role field
            if role not in ['admin', 'moderator']:
                return Response({
                    "success" : False,
                    "message": "Invalid role. Role must be either 'admin' or 'moderator'."
                }, status=status.HTTP_400_BAD_REQUEST)

            # If the role is admin, create a superuser, otherwise create a moderator
            if role == 'admin':
                user = UserModel.objects.create_superuser(
                    email=serializer.validated_data['email'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    password=serializer.validated_data['password'],
                    role=serializer.validated_data['role'],
                    is_active=True,
                    is_staff=True,
                    is_superuser=True,
                    has_approval=True
                )
            else:
                user = UserModel.objects.create_moderator(
                    email=serializer.validated_data['email'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    password=serializer.validated_data['password'],
                    role=serializer.validated_data['role'],
                    is_active=True,
                    is_staff=True,
                    is_superuser=False,
                    has_approval=True
                )

            response_data = {
                'success': True,
                'message': f'{user.role.capitalize()} created successfully.',
                'uid': user.uid,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'has_approval': user.has_approval
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            print(ex)
            return Response({
                "success" : False,
                "message" : "Something went wrong. Please try again.",
            }, status = status.HTTP_400_BAD_REQUEST)
