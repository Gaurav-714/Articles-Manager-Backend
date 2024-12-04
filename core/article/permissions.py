from rest_framework.permissions import BasePermission

# Custom permissions for Admin to have full access over content
class AdminPermissions(BasePermission):
    def has_permission(self, request, view):
            return request.user.is_superuser and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
            return request.user.is_superuser and request.user.role == 'admin'

# Custom permissions for Moderator to have full access to manage the content
class ModeratorPermissions(BasePermission):
    def has_permission(self, request, view):
            return request.user.is_superuser and request.user.role == 'moderator'

    def has_object_permission(self, request, view, obj):
            return request.user.is_superuser and request.user.role == 'moderator'


class ArticleAndCommentPermissions(BasePermission):
    """
    Custom permissions for Article and Comment:
    - Any authenticated user can view articles and comments (GET).
    - Only users with `has_approval` can create articles and comments (POST).
    - Only the author of the article/comment can modify/delete it (PUT, PATCH, DELETE).
    - Admins and moderators have full access (handled by a separate permission).
    """

    def has_permission(self, request, view):
        # Allow viewing for any authenticated user
        if request.method == 'GET':
            return True
        # Allow creation only if the user has approval
        elif request.method == 'POST':
            return request.user.has_approval
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated
        return False


    def has_object_permission(self, request, view, obj):
        # Allow read-only access for any authenticated user
        if request.method == 'GET':
            return True
        if request.method in ['PUT','PATCH','DELETE']:
            # Allow authors to modify/delete their own articles
            return obj.author == request.user
        return False
        


class CategoryAndTagPermissions(BasePermission):
    """
    Custom permissions for Category and Tag:
    - Any authenticated user can view Categories/Tags (GET).
    - Only users with `has_approval` can create Categories/Tags (POST).
    - Admins and moderators have full access (handled by a separate permissions).
    """
    def has_permission(self, request, view):
        # Allow viewing for any authenticated user
        if request.method == 'GET':
            return True
        # Allow creation only if the user has approval
        elif request.method == 'POST':
            return request.user.has_approval
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for any authenticated user
        if request.method == 'GET':
            return True
        return False

