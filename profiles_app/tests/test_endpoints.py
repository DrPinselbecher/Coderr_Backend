from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class ProfileEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max_mustermann",
            email="max@business.de",
            password="examplePassword",
            first_name="Max",
            last_name="Mustermann",
        )
        self.token = Token.objects.create(user=self.user)
        self.url = f"/api/profile/{self.user.id}/"

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)

        # müssen "" sein, nicht null
        for field in ["location", "tel", "description", "working_hours"]:
            self.assertIsNotNone(response.data[field])