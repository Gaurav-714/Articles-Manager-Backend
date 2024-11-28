from django.urls import path
from .views import *

urlpatterns = [
    path('approval-request/<uuid:uid>', HandleApprovalRequestView.as_view()),
]