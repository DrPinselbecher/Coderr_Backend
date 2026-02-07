# offers_app/api/serializers.py
from rest_framework import serializers
from offers_app.models import Offer

class OfferDetailLinkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.CharField()

class OfferUserDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    username = serializers.CharField()

class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", read_only=True)
    details = serializers.SerializerMethodField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at",
            "details", "min_price", "min_delivery_time", "user_details",
        ]

    def get_details(self, obj):
        request = self.context.get("request")
        return [
            {
                "id": d.id,
                "url": request.build_absolute_uri(f"/api/offerdetails/{d.id}/") if request else f"/api/offerdetails/{d.id}/",
            }
            for d in obj.details.all()
        ]

    def get_user_details(self, obj):
        u = obj.user
        return {
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "username": u.username,
        }
