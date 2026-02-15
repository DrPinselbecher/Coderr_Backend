from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from reviews_app.models import Review


class ReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["business_user", "rating", "description"]

    def validate_business_user(self, value):
        profile = getattr(value, "profile", None)
        if not profile or profile.type != "business":
            raise serializers.ValidationError("business_user must be a business user.")
        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        business_user = attrs["business_user"]
        reviewer = request.user

        if Review.objects.filter(
            business_user=business_user,
            reviewer=reviewer
        ).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this business user."}
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        return Review.objects.create(
            business_user=validated_data["business_user"],
            reviewer=request.user,
            rating=validated_data["rating"],
            description=validated_data.get("description", ""),
        )


class ReviewPatchSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ["rating", "description"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value


class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
