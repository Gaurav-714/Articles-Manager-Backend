from rest_framework.permissions import BasePermission

# Custom permission to only allow "Admin" to perform certain actions.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser and request.user.role == 'admin':
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser and request.user.role == 'admin':
            return True
        return False

# Custom permission to only allow "Admin" to perform certain actions.
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_staff and request.user.role == 'moderator':
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff and request.user.role == 'moderator':
            return True
        return False
