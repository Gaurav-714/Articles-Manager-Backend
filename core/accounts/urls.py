from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('verify-otp', VerifyOTPView.as_view()),
    path('resend-otp', SendMailWithOTPView.as_view()),
    path('forgot-password', SendMailWithOTPView.as_view()),
    path('set-new-password', SetNewPasswordView.as_view()),
    path('create-role', CreateAdminOrModeratorView.as_view()),
    path('request-approval', SubmitApprovalRequestView.as_view()),
]
