from rest_framework import permissions


class IsAdminOrSuperuserOrReadOnly(permissions.BasePermission):
    """Права админа, суперюзера для добавления категорий, жанров и
    произведений или только чтение для всех пользователей."""

    def has_permission(self, request, view):
        user = request.user
        return (request.method in permissions.SAFE_METHODS
                or user.is_admin
                or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (request.method in permissions.SAFE_METHODS
                or user.is_admin
                or user.is_superuser)


class IsAdminOrSuperuser(permissions.BasePermission):
    """Права админа, суперюзера для просмотра пользователей и
    изменения ролей."""

    def has_permission(self, request, view):
        user = request.user
        return user.is_admin or user.is_superuser

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_admin or user.is_superuser


class IsAdminModerAuthorOrReadonly(permissions.BasePermission):
    """Права админа, модератора, автора для добавления/редактирования
    отзывов и комментариев."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (request.method in permissions.SAFE_METHODS
                or user.is_superuser
                or user.is_admin
                or user.is_moderator
                or user == obj.author)
