"""
Custom permissions for orders API:
- customer-only order creation
- business-only order updates
- object-level ownership for business side
"""

from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Allow access only to authenticated users with a customer profile.
    """

    message = "Only customer users are allowed to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        if not profile:
            return False

        return profile.type == "customer"


class IsBusinessUser(BasePermission):
    """
    Allow access only to authenticated users with a business profile.
    """

    message = "Only business users are allowed to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        if not profile:
            return False

        return profile.type == "business"


class IsOrderBusinessOwner(BasePermission):
    """
    Object-level permission: only the business_user of an order can modify it.
    """

    message = "Only the business owner of this order can modify it."

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.business_user_id == request.user.id
        )
