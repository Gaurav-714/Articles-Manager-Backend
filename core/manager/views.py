from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.permissions import IsAdmin, IsModerator
from .serializers import ApprovalRequestSerializer
from .models import WriteApprovalRequest


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

