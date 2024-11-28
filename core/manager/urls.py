from django.urls import path
from .views import *

urlpatterns = [
    path('create-role', CreateAdminOrModeratorView.as_view()),
    path('change-role', ChangeRoleView.as_view()),
    path('approval-request/<uuid:uid>', HandleApprovalRequestView.as_view()),
]