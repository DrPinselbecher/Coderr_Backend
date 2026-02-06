# profiles_app/tests/test_views.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles_app.models import Profile

User = get_user_model()


class ProfileViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max",
            email="max@test.de",
            password="pass12345",
            first_name="Max",
            last_name="Mustermann",
        )
        Profile.objects.create(user=self.user, type="business")
        self.token = Token.objects.create(user=self.user)

        self.list_url = reverse("profile-list")

    def test_profiles_root_requires_auth(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profiles_root_redirects_to_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        res = self.client.get(reverse("profile-list"), follow=False)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertEqual(res["Location"], f"{self.user.id}/")

    def test_get_own_profile_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        url = reverse("profile-detail", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], self.user.id)


class ProfileRedirectViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", email="u1@test.de", password="pass12345")
        Profile.objects.create(user=self.user, type="customer")
        self.token = Token.objects.create(user=self.user)

        self.url = reverse("profile-redirect")

    def test_redirect_requires_auth(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_redirect_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        res = self.client.get(self.url, follow=False)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertEqual(res["Location"], f"{self.user.id}/")


class BusinessCustomerListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auth", email="auth@test.de", password="pass12345")
        self.token = Token.objects.create(user=self.user)

        u_biz = User.objects.create_user(username="biz", email="biz@test.de", password="pass12345")
        Profile.objects.create(user=u_biz, type="business")

        u_cus = User.objects.create_user(username="cus", email="cus@test.de", password="pass12345")
        Profile.objects.create(user=u_cus, type="customer")

        self.business_url = reverse("business-profile-list")
        self.customer_url = reverse("customer-profile-list")

    def test_business_requires_auth(self):
        res = self.client.get(self.business_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_requires_auth(self):
        res = self.client.get(self.customer_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_list_only_business(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        res = self.client.get(self.business_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["type"] == "business" for p in res.json()))

    def test_customer_list_only_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        res = self.client.get(self.customer_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["type"] == "customer" for p in res.json()))
