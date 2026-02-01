from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationEndpointTests(APITestCase):
    def test_register_success(self):
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

        self.assertTrue(User.objects.filter(username=payload["username"]).exists())


class RegistrationEndpointNegativeTests(APITestCase):
    def test_register_password_mismatch(self):
        url = reverse("registration")
        payload = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "wrongPassword",
            "type": "customer",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_existing_username(self):
        existing_user = User.objects.create_user(
            username="existingUser",
            email="example@mail.de",
            password="examplePassword",
        )
        url = reverse("registration")
        payload = {
            "username": existing_user.username,
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginEndpointTests(APITestCase):

    def setUp(self):
        self.password = "examplePassword"
        self.user = User.objects.create_user(
            username="exampleUsername",
            email="example@mail.de",
            password=self.password,
        )

    def test_login_success_returns_token_and_user_data(self):
        url = reverse("login")
        payload = {
            "username": self.user.username,
            "password": self.password,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["user_id"], self.user.id)

        self.assertTrue(Token.objects.filter(user=self.user).exists())
        

class LoginEndpointNegativeTests(APITestCase):
    def setUp(self):
        self.password = "examplePassword"
        self.user = User.objects.create_user(
            username="exampleUsername",
            email="example@mail.de",
            password=self.password,
        )
        self.url = reverse("login")

    def test_login_fails_with_wrong_password(self):
        payload = {"username": self.user.username, "password": "wrongPassword"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_with_missing_password(self):
        payload = {"username": self.user.username}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_with_missing_username(self):
        payload = {"password": self.password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_fails_with_nonexistent_username(self):
        payload = {"username": "nonexistentUser", "password": self.password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)