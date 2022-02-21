from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission, Group
from rest_framework import permissions, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response

from foodapp.models import CustomUser


class Res_ownerAuthenticationPermission(permissions.BasePermission):
    ADMIN_ONLY_AUTH_CLASSES = [BasicAuthentication, ]

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_owner:
            return user.is_superuser or \
                   not any(isinstance(request._authenticator, x) for x in self.ADMIN_ONLY_AUTH_CLASSES)
        return False

class EnduserAuthenticationPermission(permissions.BasePermission):
    ADMIN_ONLY_AUTH_CLASSES = [BasicAuthentication, ]

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_enduser:
            return user.is_superuser or \
                   not any(isinstance(request._authenticator, x) for x in self.ADMIN_ONLY_AUTH_CLASSES)
        return False

class adminuserAuthenticationPermission(permissions.BasePermission):
    ADMIN_ONLY_AUTH_CLASSES = [BasicAuthentication, ]

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_staff and user.is_superuser:
            return user.is_superuser or \
                   not any(isinstance(request._authenticator, x) for x in self.ADMIN_ONLY_AUTH_CLASSES)
        return False


