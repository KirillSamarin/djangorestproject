from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsModer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff

class IsNotModer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff

class IsOwnerOrModer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff