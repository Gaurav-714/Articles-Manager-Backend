from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'view-requests', ApprovalRequestsListView, basename='article')

urlpatterns = [
    path('create-role/', CreateAdminOrModeratorView.as_view()),
    path('change-role/', ChangeRoleView.as_view()),
    path('handle-request/<uuid:uid>/', HandleApprovalRequestView.as_view()),
    path('', include(router.urls)),
]