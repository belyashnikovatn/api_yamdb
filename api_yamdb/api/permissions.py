from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """GET-запрос доступен всем, запросы на запись доступны только admin."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminOrSuperuser(permissions.BasePermission):
    """Любые запросы доступны только аутентифицированному админу."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """Общие разрешения для Автора, Модератора, и Админа."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )
