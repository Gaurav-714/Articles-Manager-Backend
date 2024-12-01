from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings

from article.pagination import CustomPagination
from .serializers import ManageUserSerializer, ChangeRoleSerializer, ApprovalRequestSerializer
from .permissions import IsAdmin, IsModerator
from .filters import UsersFilter, RequestsFilter
from .models import WriteApprovalRequest

UserModel = get_user_model()

# Viewset to manage all the users by the Admin (GET, POST, PUT, PATCH, DELETE)
class ManageUserView(viewsets.ModelViewSet):
    queryset = UserModel.objects.all().order_by('first_name')
    serializer_class = ManageUserSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    # Pagination, Filtering and Searching
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = UsersFilter
    search_fields = ['email', 'first_name', 'last_name', 'role', 'has_approval']


# View to create new Admin or Moderator
class CreateAdminOrModeratorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]  # Only Admins can access this view

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            role = data.get('role', '')

            serializer = ManageUserSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    "success" : False,
                    "message": "Invalid data.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has admin permissions to create other admins or moderators
            if request.user.role != 'admin':
                raise PermissionDenied("You do not have permission to perform this action.")
            
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
            subject = "Account Registered On Articles Application"
            message = render_to_string('confirmationMail.html',{
                'user': user,
                'password': request.data['password']
            })
            recipient_list = [user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            print(ex)
            return Response({
                "success" : False,
                "message" : "Something went wrong. Please try again.",
            }, status = status.HTTP_400_BAD_REQUEST)


# View change role of an existing user
class ChangeRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]  # Only Admins can access this view

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            role = data.get('role')

            serializer = ChangeRoleSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    "success" : False,
                    "message": "Invalid data.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has admin permissions to create other admins or moderators
            if request.user.role != 'admin':
                raise PermissionDenied("You do not have permission to perform this action.")
            
            # Validate the role field
            if role not in ['admin', 'moderator']:
                return Response({
                    "success" : False,
                    "message": "Invalid role. Role must be either 'admin', 'moderator'."
                }, status=status.HTTP_400_BAD_REQUEST)

            user_obj = UserModel.objects.filter(email=data['email']).first()
            user_obj.role = serializer.validated_data['role']
            user_obj.is_active=True,
            user_obj.is_staff=True,
            user_obj.has_approval=True

             # If the role is admin, assign a superuser, otherwise create a moderator
            if role == 'admin':
                user_obj.is_superuser=True,
                user_obj.save()
            else:
                user_obj.is_superuser=False,
                user_obj.save()

            response_data = {
                'success': True,
                'message': f'{user_obj.role.capitalize()} changed successfully.',
                'uid': user_obj.uid,
                'email': user_obj.email,
                'first_name': user_obj.first_name,
                'last_name': user_obj.last_name,
                'role': user_obj.role,
                'is_active': user_obj.is_active,
                'is_staff': user_obj.is_staff,
                'is_superuser': user_obj.is_superuser,
                'has_approval': user_obj.has_approval
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            print(ex)
            return Response({
                "success" : False,
                "message" : "Something went wrong. Please try again.",
            }, status = status.HTTP_400_BAD_REQUEST)


# View to list out all the pending requests for writing articles
class ApprovalRequestsListView(viewsets.ReadOnlyModelViewSet):
    queryset = WriteApprovalRequest.objects.filter(status='pending').order_by('-created_at')
    serializer_class = ApprovalRequestSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, (IsAdmin | IsModerator)]

    # Pagination and Filtering
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RequestsFilter


# View to handle user's requests by the Moderator/Admin (approve/reject)
class HandleApprovalRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, (IsAdmin | IsModerator)]

    def post(self, request, uid):        
        try:
            action = request.data.get('action')  # "approve" or "reject"
            if not action or action not in ['approve','reject']:
                return Response({
                    "success": False,
                    "error": "Please specify action as 'approve' or 'reject'."
                }, status=status.HTTP_400_BAD_REQUEST)

            approval_request = WriteApprovalRequest.objects.get(uid=uid)
            if action == 'approve':
                approval_request.status = 'approved'
                approval_request.user.has_approval = True
                approval_request.user.save()
                approval_request.save()

                subject = "Regarding Your Approval Request On Articles Application"
                message = "Your request has been approved. Now you can write and publish your articles on the application."
                recipient_list = [approval_request.user.email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

                return Response({
                    "success": True,
                    "message": "Request approved successfully."
                }, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                approval_request.status = 'rejected'
                approval_request.save()

                subject = "Regarding Your Approval Request On Articles Application"
                message = "Sorry, your request has been rejected. You are not allowed to publish your articles on the application."
                recipient_list = [approval_request.user.email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

                return Response({
                    "success": True,
                    "message": "Request rejected successfully."
                }, status=status.HTTP_200_OK)
            
        except WriteApprovalRequest.DoesNotExist:
            return Response({
                "success": False,
                "error": "Request not found."
            }, status=status.HTTP_404_NOT_FOUND)
