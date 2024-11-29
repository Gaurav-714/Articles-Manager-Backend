from django_filters import rest_framework as filters
from .models import WriteApprovalRequest

class RequestsFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = WriteApprovalRequest
        fields = ['status']