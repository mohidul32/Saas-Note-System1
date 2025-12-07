from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.workspace.company == request.user.company and request.user.is_owner()


class IsOwnerOfWorkspace(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_owner()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.workspace.company == request.user.company and request.user.is_owner()


class CanAccessNote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Public notes can be accessed by anyone
        if obj.note_type == 'public' and not obj.is_draft:
            return True

        # Private notes and drafts only by company members
        if request.user.is_authenticated:
            return obj.workspace.company == request.user.company

        return False