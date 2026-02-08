from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsBusinessUser(BasePermission):
    message = "Only business users can create offers."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        if not profile:
            return False

        return profile.type == "business"
    

class IsOfferOwner(BasePermission):
    message = "Only the owner of this offer can modify or delete it."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and obj.user_id == request.user.id
