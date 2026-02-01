from rest_framework import serializers
from profiles_app.models import Profile


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
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "file",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "username",
            "type",
            "file",
            "created_at",
        ]

    def update(self, instance, validated_data):  # Wird aufgerufen, wenn ein bestehendes Profile aktualisiert wird (PUT/PATCH)
        user_data = validated_data.pop("user", {})  # Holt verschachtelte User-Daten (aus source="user.*") raus und entfernt sie aus validated_data

        for attr in ("first_name", "last_name", "email"):  # Geht die User-Felder durch, die wir aktualisieren wollen
            setattr(instance.user, attr, user_data[attr])  # Setzt z.B. instance.user.first_name = user_data["first_name"] (dynamisch per Attributname)
        instance.user.save()  # Speichert die Änderungen am User in der Datenbank

        return super().update(instance, validated_data)  # Aktualisiert danach die restlichen Profile-Felder (location, tel, ...) und gibt das aktualisierte Profil zurück

