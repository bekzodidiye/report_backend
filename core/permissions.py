from rest_framework.permissions import BasePermission, IsAuthenticated

class IsCitizen(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'citizen'

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'moderator' or request.user.is_staff)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)

class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.user == request.user or request.user.role in ['moderator', 'admin']

class IsVerifiedUser(BasePermission):
    """Only trusted_inspector level users can verify"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.level == 'trusted_inspector'
        )
