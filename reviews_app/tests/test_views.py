from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewsViewsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.list_url = reverse("reviews-list")

    def test_ordering_by_rating(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=2, description="a")
        customer2 = User.objects.create_user(username="cust2", password="pw123456")
        Profile.objects.create(user=customer2, type="customer")
        Review.objects.create(business_user=self.business, reviewer=customer2, rating=5, description="b")

        self.client.login(username="cust", password="pw123456")
        res = self.client.get(self.list_url, {"ordering": "rating"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        ratings = [item["rating"] for item in data]
        self.assertEqual(ratings, sorted(ratings))
