from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationViewTests(APITestCase):
    def test_registration_creates_token_and_returns_expected_payload(self):
        url = reverse("registration")
        payload = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertIn("user_id", response.data)

        user = User.objects.get(username=payload["username"])
        self.assertTrue(Token.objects.filter(user=user).exists())