from django.test import TestCase
from django.contrib.auth import get_user_model

from user_auth_app.api.serializers import RegistrationSerializer

User = get_user_model()


class RegistrationSerializerTests(TestCase):
    def test_valid_data_creates_user_and_hashes_password(self):
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer",
        }

        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertIsInstance(user, User)
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_password_mismatch_returns_error_on_repeated_password(self):
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "DIFFERENT",
            "type": "customer",
        }

        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("repeated_password", serializer.errors)
