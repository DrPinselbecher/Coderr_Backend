from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from profiles_app.models import Profile

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
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.token = Token.objects.create(user=self.user)
        self.url = reverse("profile-detail", args=[self.user.profile.id])

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_response_contract_ordered(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        self.assertEqual(list(response.data.keys()), expected_fields)

    def test_profile_fields_are_not_null(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        not_null_fields = [
            "user",
            "username",
            "email",
            "type",
            "created_at",
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]

        for field in not_null_fields:
            with self.subTest(field=field):
                self.assertIsNotNone(response.data[field])


class ProfileDetailEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max_mustermann",
            email="max@mustermann.de",
            password="examplePassword",
            first_name="Max",
            last_name="Mustermann",
        )
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.token = Token.objects.create(user=self.user)
        self.url = reverse("profile-list")

    def test_profile_redirect_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_redirect_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, f"{self.user.id}/")


class ProfileEndpointNegativeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max_mustermann",
            email="max@mustermann.de",
            password="examplePassword",
            first_name="Max",
            last_name="Mustermann",
        )
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.token = Token.objects.create(user=self.user)
        self.url = reverse("profile-list")

    def test_profile_redirect_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileDetailEndpointNegativeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max_mustermann",
            email="max@mustermann.de",
            password="examplePassword",
            first_name="Max",
            last_name="Mustermann",
        )
        self.profile = Profile.objects.create(user=self.user, type="business")
        self.token = Token.objects.create(user=self.user)
        self.url = reverse("profile-detail", args=[9999])

    def test_get_profile_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ProfileDetailPermissionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user_one",
            email="user@one.de",
            password="passwordOne",
            first_name="User",
            last_name="One",
        )
        self.profile1 = Profile.objects.create(user=self.user1, type="customer")
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(
            username="user_two",
            email="user@two.de",
            password="passwordTwo",
            first_name="User",
            last_name="Two",
        )
        self.profile2 = Profile.objects.create(user=self.user2, type="business")
        self.token2 = Token.objects.create(user=self.user2)

        self.url1 = reverse("profile-detail", args=[self.user1.profile.id])
        self.url2 = reverse("profile-detail", args=[self.user2.profile.id])

    def test_user_cannot_access_other_users_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_user_can_access_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user1.username)


