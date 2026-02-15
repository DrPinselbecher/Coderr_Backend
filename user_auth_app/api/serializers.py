"""
Authentication + registration serializers.

Includes:
- RegistrationSerializer: creates User + Profile (customer/business) in one transaction
- EmailAuthTokenSerializer: validates username/password via Django authenticate()
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from profiles_app.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Registration serializer for creating a new user account.

    Input:
        - username: str
        - email: str
        - password: str
        - repeated_password: str (must match password)
        - type: "customer" | "business" (stored on Profile)

    Output:
        - returns created User instance
    """

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=["customer", "business"], write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]

    def validate(self, attrs):
        """
        Ensure passwords match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        """
        Create User and Profile atomically.
        """
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        profile_type = validated_data.pop("type")

        with transaction.atomic():
            user = User(
                username=validated_data["username"],
                email=validated_data["email"],
            )
            user.set_password(password)
            user.save()

            Profile.objects.create(
                user=user,
                type=profile_type,
            )

        return user


class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Login serializer using username + password via Django authenticate().

    Notes:
        - returns `user` in validated_data on success
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Authenticate user with provided credentials.
        """
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )

        if not user:
            raise serializers.ValidationError("Invalid username/password.")

        attrs["user"] = user
        return attrs
