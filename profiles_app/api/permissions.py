"""
Custom permissions for profile resources.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Read-only access for everyone who passes base permissions,
    write access only for the owner.

    Assumption:
        - obj is a Profile instance with a `.user` FK to auth user.
    """

    message = "You can only modify your own profile."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
