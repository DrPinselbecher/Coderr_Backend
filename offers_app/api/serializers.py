"""
Serializers for offers and offer details, including:
- list/retrieve payloads
- create payload validation (3 details required: basic/standard/premium)
- partial update payload for offer and nested details by offer_type
"""

from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailLinkSerializer(serializers.Serializer):
    """
    Minimal link representation for OfferDetail.
    """

    id = serializers.IntegerField()
    url = serializers.CharField()


class OfferUserDetailsSerializer(serializers.Serializer):
    """
    Public user fields embedded in offer responses.
    """

    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    username = serializers.CharField()


class OfferListSerializer(serializers.ModelSerializer):
    """
    Offer list serializer including:
    - details links
    - annotated fields (min_price, min_delivery_time)
    - embedded user_details
    """

    user = serializers.IntegerField(source="user_id", read_only=True)
    details = serializers.SerializerMethodField()
    min_price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_details(self, obj):
        """
        Build simple relative URLs for offer details.
        """
        return [{"id": d.id, "url": f"/offerdetails/{d.id}/"} for d in obj.details.all()]

    def get_user_details(self, obj):
        """
        Embed basic user display fields.
        """
        u = obj.user
        return {
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "username": u.username,
        }


class OfferDetailCreateSerializer(serializers.ModelSerializer):
    """
    Input serializer for creating OfferDetail items.
    """

    class Meta:
        model = OfferDetail
        fields = [
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Input serializer for creating an offer with exactly 3 details:
    basic, standard, premium (unique offer_type).
    """

    details = OfferDetailCreateSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["title", "image", "description", "details"]

    def validate_details(self, value):
        """
        Enforce:
        - exactly 3 details
        - unique offer_type
        - must contain {basic, standard, premium}
        """
        if len(value) != 3:
            raise serializers.ValidationError("An offer must contain exactly 3 details.")

        types = [d.get("offer_type") for d in value]
        if len(set(types)) != 3:
            raise serializers.ValidationError("offer_type must be unique across details.")

        required = {"basic", "standard", "premium"}
        if set(types) != required:
            raise serializers.ValidationError(
                "Details must include basic, standard and premium."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Create Offer and associated OfferDetail rows in a single transaction.
        """
        details_data = validated_data.pop("details")
        request = self.context["request"]

        offer = Offer.objects.create(user=request.user, **validated_data)

        OfferDetail.objects.bulk_create([OfferDetail(offer=offer, **d) for d in details_data])

        return offer


class OfferDetailResponseSerializer(serializers.ModelSerializer):
    """
    Output serializer for OfferDetail.
    """

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferResponseSerializer(serializers.ModelSerializer):
    """
    Output serializer for Offer with nested details.
    """

    details = OfferDetailResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Offer retrieve serializer including annotated fields and absolute detail URLs.
    """

    user = serializers.IntegerField(source="user_id", read_only=True)
    details = serializers.SerializerMethodField()
    min_price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_details(self, obj):
        """
        Build absolute URLs to /api/offerdetails/<id>/ based on request host.
        """
        request = self.context.get("request")
        base = request.build_absolute_uri("/")[:-1] if request else ""
        return [{"id": d.id, "url": f"{base}/api/offerdetails/{d.id}/"} for d in obj.details.all()]


class OfferDetailPatchSerializer(serializers.Serializer):
    """
    Patch payload for OfferDetail, addressed by offer_type.
    """

    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES)

    title = serializers.CharField(required=False)
    revisions = serializers.IntegerField(required=False, min_value=0)
    delivery_time_in_days = serializers.IntegerField(required=False, min_value=0)
    price = serializers.DecimalField(required=False, max_digits=7, decimal_places=2)
    features = serializers.ListField(child=serializers.CharField(), required=False)


class OfferPatchSerializer(serializers.ModelSerializer):
    """
    Patch payload for Offer including optional nested details patch list.
    """

    details = OfferDetailPatchSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ["title", "image", "description", "details"]

    def validate_details(self, value):
        """
        Enforce unique offer_type within patch list.
        """
        types = [d.get("offer_type") for d in value]
        if len(types) != len(set(types)):
            raise serializers.ValidationError("offer_type must be unique in details.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for field, val in validated_data.items():
            setattr(instance, field, val)
        instance.save()

        if details_data is not None:
            details_by_type = {d.offer_type: d for d in instance.details.all()}

            for patch in details_data:
                offer_type = patch.pop("offer_type", None)
                if not offer_type:
                    raise serializers.ValidationError(
                        {"details": "offer_type is required for each detail patch."}
                    )

                detail = details_by_type.get(offer_type)
                if not detail:
                    raise serializers.ValidationError(
                        {"details": f"OfferDetail with offer_type '{offer_type}' not found."}
                    )

                for field, val in patch.items():
                    setattr(detail, field, val)
                detail.save()

        return instance
