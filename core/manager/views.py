from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import PermissionDenied

from accounts.models import UserModel
from manager.permissions import IsAdmin, IsModerator
from .serializers import RoleCreateSerializer, ChangeRoleSerializer, ApprovalRequestSerializer
from .models import WriteApprovalRequest


class CreateAdminOrModeratorView(APIView):
    permission_classes = [IsAdmin]  # Only Admins can access this view

    def post(self, request, *args, **kwargs):
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
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            print(ex)
            return Response({
                "success" : False,
                "message" : "Something went wrong. Please try again.",
            }, status = status.HTTP_400_BAD_REQUEST)


class ChangeRoleView(APIView):
    permission_classes = [IsAdmin]  # Only Admins can access this view

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


class HandleApprovalRequestView(APIView):
    permission_classes = [IsAdmin, IsModerator]
    authentication_classes = [JWTAuthentication]

    def get(self, request):        
        requests = WriteApprovalRequest.objects.filter(status='pending')
        serializer = ApprovalRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                return Response({
                    "success": True,
                    "message": "Request approved successfully."
                }, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                approval_request.status = 'rejected'
                approval_request.save()
                return Response({
                    "success": True,
                    "message": "Request rejected successfully."
                }, status=status.HTTP_200_OK)
            
        except WriteApprovalRequest.DoesNotExist:
            return Response({
                "success": False,
                "error": "Request not found."
            }, status=status.HTTP_404_NOT_FOUND)
