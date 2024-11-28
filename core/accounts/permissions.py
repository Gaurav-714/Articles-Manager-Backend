from rest_framework.permissions import BasePermission

# Custom permission to only allow "Admin" to perform certain actions.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user and request.user.role == 'admin' and request.user.is_authenticated
        except:
            return False

# Custom permission to only allow "Moderator" to perform certain actions.
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user and request.user.role == 'moderator' and request.user.is_authenticated
        except:
            return False
