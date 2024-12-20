from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from .models import WriteApprovalRequest

UserModel = get_user_model()


class ManageUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = UserModel
        fields = ['uid', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active', 'is_staff', 'is_superuser', 'has_approval']
        read_only_fields = ['uid', 'is_active', 'is_staff', 'is_superuser', 'has_approval']        

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value

    def validate(self, data):
        try:
            if 'email' in data:
                validate_email(data['email'])
                if UserModel.objects.filter(email=data['email']).exists():
                    raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        except ValidationError:
            raise ValidationError("Please provide a valid email address.")
        
        return data


class ChangeRoleSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = UserModel
        fields = ['uid', 'email', 'role']
        read_only_fields = ['uid', 'is_active', 'is_staff', 'is_superuser', 'has_approval']        

    def validate(self, data):
        try:
            validate_email(data['email'])
        except ValidationError:
            raise ValidationError("Please provide a valid email address.")
        
        if not UserModel.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'No user with this email exists.'})
        return data


class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriteApprovalRequest
        fields = ['uid', 'user', 'status', 'message', 'created_at', 'updated_at']

    def validate(self, data):
        if data['user'].has_approval:
            raise ValidationError("You are already approved to write articles.")
        return data