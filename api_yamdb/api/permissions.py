from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_admin
            and user.is_authenticated
        )


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_moderator
            and user.is_authenticated
        )


class IsAuthUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj.author

# Нужен ли вообще безопасный метод для всего ? что бы был просто ...
# class ReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.method in permissions.SAFE_METHODS

#     def has_object_permission(self, request, view, obj):
#         return request.method in permissions.SAFE_METHODS
