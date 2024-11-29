from rest_framework.permissions import BasePermission

# Custom permission to allow only "Admin" to perform certain actions.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in ['GET']:
                return True
            elif request.user.is_superuser and request.user.role == 'admin':
                return True
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser and request.user.role == 'admin':
            return True
        return obj.author == request.user # Users can only edit or delete their own article/category/tag


# Custom permission to allow only "Moderator" to perform certain actions.
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in ['GET']:
                return True
            elif request.user.is_staff or request.user.role == 'moderator':
                return True
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == 'moderator':
            return True
        return obj.author == request.user  # Users can only edit or delete their own article/category/tag
