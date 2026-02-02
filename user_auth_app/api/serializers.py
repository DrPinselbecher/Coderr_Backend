from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from profiles_app.models import Profile
from django.db import transaction


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=["customer", "business"], write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
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
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )

        if not user:
            raise serializers.ValidationError("Invalid username/password.")

        attrs["user"] = user
        return attrs
