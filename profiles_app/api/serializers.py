from rest_framework import serializers
from profiles_app.models import Profile


class NullToEmptyStringMixin:
    non_null_fields = []

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field in self.non_null_fields:
            if data.get(field) is None:
                data[field] = ""

        return data


class BaseProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "username",
            "type",
            "file",
            "created_at",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        for attr in ("first_name", "last_name", "email"):
            if attr in user_data:
                setattr(instance.user, attr, user_data[attr])

        instance.user.save()
        return super().update(instance, validated_data)
    

class ProfileSummarySerializer(
    NullToEmptyStringMixin,
    BaseProfileSerializer
):
    non_null_fields = [
        "first_name",
        "last_name",
        "location",
        "tel",
        "description",
        "working_hours",
    ]

    class Meta(BaseProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
