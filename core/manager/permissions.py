from rest_framework.permissions import BasePermission


# Custom permission to only allow "Admin" to perform certain actions.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and has an 'admin' role
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Admins can access all articles
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        return obj.author == request.user # Users can only edit or delete their own articles


# Custom permission to only allow "Moderator" to perform certain actions.
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and has a 'moderator' role
        if request.user.is_authenticated and request.user.role == 'moderator':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Moderators can access all articles
        if request.user.role == 'moderator':
            return True
        return obj.author == request.user # Users can only edit or delete their own articles
