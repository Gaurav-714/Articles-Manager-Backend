from rest_framework import serializers
from .models import WriteApprovalRequest

class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriteApprovalRequest
        fields = ['uid', 'user', 'status', 'message', 'created_at', 'updated_at']
