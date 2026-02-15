# core/tests/test_endpoints.py
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review


class BaseInfoEndpointsTests(APITestCase):
    def setUp(self):
        self.url = reverse("base-info")

        self.business_user = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business_user, type="business")

        self.customer_user = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer_user, type="customer")

        Offer.objects.create(user=self.business_user, title="Offer 1", description="d")
        Offer.objects.create(user=self.business_user, title="Offer 2", description="d")

        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="x",
        )

    def test_base_info_no_auth_required(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_base_info_payload_keys(self):
        res = self.client.get(self.url)
        data = res.json()

        self.assertIn("review_count", data)
        self.assertIn("average_rating", data)
        self.assertIn("business_profile_count", data)
        self.assertIn("offer_count", data)

    def test_base_info_values(self):
        res = self.client.get(self.url)
        data = res.json()

        self.assertEqual(data["review_count"], 1)
        self.assertEqual(data["average_rating"], 5.0)
        self.assertEqual(data["business_profile_count"], 1)
        self.assertEqual(data["offer_count"], 2)

    def test_average_rating_rounded_one_decimal(self):
        customer2 = User.objects.create_user(username="cust2", password="pw123456")
        Profile.objects.create(user=customer2, type="customer")

        Review.objects.create(
            business_user=self.business_user,
            reviewer=customer2,
            rating=4,
            description="y",
        )

        res = self.client.get(self.url)
        data = res.json()

        self.assertEqual(data["average_rating"], 4.5)
