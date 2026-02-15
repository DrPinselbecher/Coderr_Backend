"""
Orders endpoints:
- list: authenticated, returns orders where user is customer or business
- create: authenticated + customer, creates order from OfferDetail snapshot
- partial_update: authenticated + business + business owner, status-only patch
- destroy: admin-only

Additional endpoints (APIView):
- OrderCountView: count IN_PROGRESS orders for a business user
- CompletedOrderCountView: count COMPLETED orders for a business user
"""

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .permissions import IsBusinessUser, IsCustomerUser, IsOrderBusinessOwner
from .serializers import (
    OrderCreateResponseSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderStatusPatchSerializer,
    OrderUpdateResponseSerializer,
)


class OrdersViewSet(viewsets.ModelViewSet):
    """
    CRUD-like endpoint for orders.

    Notes:
        - List is scoped to the requesting user (customer OR business side).
        - Status updates are restricted to the business owner of the order.
        - Deletion is admin-only.
    """

    queryset = Order.objects.all()

    def get_queryset(self):
        """
        For list: return orders where the user is either customer or business.
        Otherwise: fall back to the base queryset.
        """
        user = self.request.user

        if self.action == "list":
            return (
                Order.objects.filter(Q(customer_user=user) | Q(business_user=user))
                .order_by("-created_at")
            )

        return Order.objects.all()

    def get_permissions(self):
        """
        Permissions by action:
            - list: authenticated
            - create: authenticated + customer
            - partial_update/update: authenticated + business + order business owner
            - destroy: authenticated + admin
        """
        if self.action == "list":
            return [IsAuthenticated()]

        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]

        if self.action in ["partial_update", "update"]:
            return [IsAuthenticated(), IsBusinessUser(), IsOrderBusinessOwner()]

        if self.action == "destroy":
            return [IsAuthenticated(), IsAdminUser()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Serializer by action.
        """
        if self.action == "create":
            return OrderCreateSerializer
        if self.action in ["partial_update", "update"]:
            return OrderStatusPatchSerializer
        return OrderListSerializer

    def create(self, request, *args, **kwargs):
        """
        Create an order by snapshotting fields from an OfferDetail.
        """
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(
            OrderCreateResponseSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Status-only patch for business owner.

        Rejects any fields other than 'status'.
        """
        allowed_keys = {"status"}
        extra_keys = set(request.data.keys()) - allowed_keys

        if extra_keys:
            return Response(
                {"detail": "Unallowed fields in request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = self.get_object()

        serializer = OrderStatusPatchSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        order.refresh_from_db(fields=["updated_at", "status"])

        return Response(
            OrderUpdateResponseSerializer(order, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class OrderCountView(APIView):
    """
    Return count of IN_PROGRESS orders for a given business user id.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id, *args, **kwargs):
        """
        Args:
            business_user_id: User PK that must belong to a business profile.

        Returns:
            {"order_count": int}
        """
        user = get_object_or_404(User, pk=business_user_id)
        profile = getattr(user, "profile", None)

        if not profile or profile.type != "business":
            return Response(status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(
            business_user_id=user.id,
            status=Order.Status.IN_PROGRESS,
        ).count()

        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    Return count of COMPLETED orders for a given business user id.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id, *args, **kwargs):
        """
        Args:
            business_user_id: User PK that must belong to a business profile.

        Returns:
            {"completed_order_count": int}
        """
        user = get_object_or_404(User, pk=business_user_id)
        profile = getattr(user, "profile", None)

        if not profile or profile.type != "business":
            return Response(status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(
            business_user_id=user.id,
            status=Order.Status.COMPLETED,
        ).count()

        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
