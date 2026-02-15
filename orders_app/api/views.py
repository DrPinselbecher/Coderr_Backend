from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .permissions import IsBusinessUser, IsCustomerUser, IsOrderBusinessOwner
from .serializers import OrderCreateSerializer, OrderListSerializer, OrderStatusPatchSerializer, OrderCreateResponseSerializer, OrderUpdateResponseSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user

        if self.action == "list":
            return (
                Order.objects
                .filter(Q(customer_user=user) | Q(business_user=user))
                .order_by("-created_at")
            )

        return Order.objects.all()

    def get_permissions(self):
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
        if self.action == "create":
            return OrderCreateSerializer
        if self.action in ["partial_update", "update"]:
            return OrderStatusPatchSerializer
        return OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(
            OrderCreateResponseSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id, *args, **kwargs):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=business_user_id)
        profile = getattr(user, "profile", None)
        
        if not profile or profile.type != "business":
            return Response(status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(
            business_user_id=user.id,
            status=Order.Status.COMPLETED,
        ).count()

        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
