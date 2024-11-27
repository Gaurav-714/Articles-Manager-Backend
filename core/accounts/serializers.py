from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

UserModel = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = UserModel
        fields = ['uid', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['uid', 'role', 'is_active', 'is_staff', 'is_superuser']

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = UserModel.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError("Account not found.")
        data['user'] = user
        return data
    
    def get_jwt_token(self, validated_data):
        user = UserModel.objects.filter(email=validated_data['email']).first()

        if user.check_password(validated_data['password']):
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return {
                "success": True,
                "message": "Logged in successfully.",
                "tokens":{
                    "refresh": str(refresh),
                    "access": str(access_token),
                }
            }
        else:
            return {
                "success": False,
                "message": "Invalid credentials.",
                "data": {}
            }
        

class RoleCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = UserModel
        fields = ['uid', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['uid', 'is_active', 'is_staff', 'is_superuser', 'has_approval']

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if UserModel.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        return data

