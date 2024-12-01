from django_filters import rest_framework as filters
from accounts.models import UserModel
from .models import WriteApprovalRequest

class UsersFilter(filters.FilterSet):
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    role = filters.CharFilter(field_name="role", lookup_expr="icontains")
    has_approval = filters.BooleanFilter(field_name="has_approval")

    class Meta:
        model = UserModel
        fields = ['email', 'first_name', 'last_name', 'role', 'has_approval']


class RequestsFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = WriteApprovalRequest
        fields = ['status']

