from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        raise MethodNotAllowed("Добавление запрещено!")
