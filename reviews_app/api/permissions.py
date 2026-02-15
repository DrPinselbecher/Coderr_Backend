"""
Custom permissions for reviews API:
- only customers can create reviews
- only the review owner can update/delete
"""

from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Allow access only to authenticated users with a customer profile.
    """

    message = "Only customer users can create reviews."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.type == "customer")


class IsReviewOwner(BasePermission):
    """
    Object-level permission: only the reviewer can modify/delete their review.
    """

    message = "Only the owner of this review can modify or delete it."

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and request.user.is_authenticated and obj.reviewer_id == request.user.id
        )
