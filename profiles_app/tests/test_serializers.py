# profiles_app/tests/test_serializers.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles_app.models import Profile
from profiles_app.api.serializers import ProfileSerializer, ProfileSummarySerializer

User = get_user_model()


class ProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max",
            email="max@test.de",
            password="pass12345",
            first_name="Max",
            last_name="Mustermann",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            type="customer",
            location="Berlin",
            tel="123",
            description="desc",
            working_hours="9-17",
        )

    def test_update_updates_nested_user_fields(self):
        serializer = ProfileSerializer(
            instance=self.profile,
            data={
                "first_name": "New",
                "last_name": "Name",
                "email": "new@test.de",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.email, "new@test.de")

    def test_update_does_not_overwrite_user_fields_if_not_provided(self):
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"location": "Hamburg"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Max")
        self.assertEqual(self.user.last_name, "Mustermann")
        self.assertEqual(self.user.email, "max@test.de")
        self.assertEqual(self.profile.location, "Hamburg")

    def test_fields_order_contract(self):
        data = ProfileSerializer(self.profile).data
        expected_fields = [
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
        self.assertEqual(list(data.keys()), expected_fields)


class ProfileSummarySerializerTests(TestCase):
    def test_none_fields_become_empty_string(self):
        user = User.objects.create_user(
            username="u2",
            email="u2@test.de",
            password="pass12345",
            first_name="",
            last_name="",
        )
        profile = Profile.objects.create(
            user=user,
            type="business",
            location="",
            tel="",
            description="",
            working_hours="",
        )

        data = ProfileSummarySerializer(profile).data

        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")
        self.assertEqual(data["location"], "")
        self.assertEqual(data["tel"], "")
        self.assertEqual(data["description"], "")
        self.assertEqual(data["working_hours"], "")


    def test_summary_includes_expected_fields_in_order(self):
        user = User.objects.create_user(
            username="u3",
            email="u3@test.de",
            password="pass12345",
            first_name="A",
            last_name="B",
        )
        profile = Profile.objects.create(user=user, type="business")

        data = ProfileSummarySerializer(profile).data
        expected_fields = [
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
        self.assertEqual(list(data.keys()), expected_fields)
