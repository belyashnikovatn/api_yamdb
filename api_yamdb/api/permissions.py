from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Делать GET-звапросы всем пользователям без авторизации.
    - Делать POST-запросы только администраторам.
    - Делать DELETE-запросы только администраторам.
    """

    def has_permission(self, request, view):
        """
        Проверяет права доступа на уровне действия.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user
                and request.user.is_authenticated
                and request.user.is_staff)


class IsAdminOrSuperuser(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Делать запросы только аутентифицированным пользователям
      с ролью admin или суперпользователю.
    - Разрешает доступ к объекту всем пользователям
      без дополнительной проверки на уровне объекта.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Делать GET, HEAD, OPTIONS-запросы всем пользователям, включая анонимных.
    - Делать POST, PUT, PATCH, DELETE-запросы только аутентифиц. пользователям.
    - Выполнять PATCH, DELETE-запросы следующим пользователям:
      - Автору объекта.
      - Модераторам.
      - Администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
