from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """Permite acesso apenas a usuários autenticados com papel de administrador."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_admin', False)
        )

class IsOwner(permissions.BasePermission):
    """Permite acesso apenas ao proprietário do objeto."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(obj, 'user', None) == request.user
        )
