from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from .manager import UserManager

class UserModel(AbstractBaseUser, PermissionsMixin):

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user',  
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user', 
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique = True, null=False)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    has_approval = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    objects = UserManager()
    
    def __str__(self):
        return f'{self.email}'



class AccountVerificationOTP(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self): 
        return (not self.used and (timezone.now() - self.created_at).total_seconds() < 600)