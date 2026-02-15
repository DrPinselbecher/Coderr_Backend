"""
Serializers for reviews API:
- list/detail output
- create with validation:
    - business_user must be a business profile
    - rating must be 1..5
    - one review per (business_user, reviewer)
- patch allows only rating/description
"""

from rest_framework import serializers

from reviews_app.models import Review


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing reviews.
    """

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
    """
    Input serializer for creating a review.
    Reviewer is always the authenticated user.
    """

    class Meta:
        model = Review
        fields = ["business_user", "rating", "description"]

    def validate_business_user(self, value):
        """
        Ensure business_user belongs to a business profile.
        """
        profile = getattr(value, "profile", None)
        if not profile or profile.type != "business":
            raise serializers.ValidationError("business_user must be a business user.")
        return value

    def validate_rating(self, value):
        """
        Ensure rating is within 1..5.
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        """
        Enforce unique review per (business_user, reviewer).
        """
        request = self.context["request"]
        business_user = attrs["business_user"]
        reviewer = request.user

        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this business user."}
            )

        return attrs

    def create(self, validated_data):
        """
        Create review; reviewer is forced to request.user.
        """
        request = self.context["request"]

        return Review.objects.create(
            business_user=validated_data["business_user"],
            reviewer=request.user,
            rating=validated_data["rating"],
            description=validated_data.get("description", ""),
        )


class ReviewPatchSerializer(serializers.ModelSerializer):
    """
    Patch serializer for rating/description only.
    """

    rating = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ["rating", "description"]

    def validate_rating(self, value):
        """
        Ensure rating is within 1..5.
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for a single review response payload.
    """

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
