"""
Serializers for orders API:
- Create flow based on OfferDetail snapshotting into Order
- List output
- Patch status only
"""

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderCreateResponseSerializer(serializers.ModelSerializer):
    """
    Response payload after creating an order.
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
        ]


class OrderUpdateResponseSerializer(serializers.ModelSerializer):
    """
    Response payload after updating an order (status changes).
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """
    List/retrieve payload for orders.
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Create payload for an order.

    Input:
        - offer_detail_id: int

    Behavior:
        - Copies (snapshots) OfferDetail fields into the Order at creation time.
    """

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context["request"]
        offer_detail = get_object_or_404(
            OfferDetail, pk=validated_data["offer_detail_id"]
        )

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status=Order.Status.IN_PROGRESS,
        )
        return order


class OrderStatusPatchSerializer(serializers.ModelSerializer):
    """
    Patch serializer for status changes only.
    """

    status = serializers.ChoiceField(choices=Order.Status.choices)

    class Meta:
        model = Order
        fields = ["status"]
