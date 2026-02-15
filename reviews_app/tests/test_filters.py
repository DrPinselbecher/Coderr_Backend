from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewsFiltersTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.customer2 = User.objects.create_user(username="cust2", password="pw123456")
        Profile.objects.create(user=self.customer2, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.business2 = User.objects.create_user(username="biz2", password="pw123456")
        Profile.objects.create(user=self.business2, type="business")

        self.r1 = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="a")
        self.r2 = Review.objects.create(business_user=self.business2, reviewer=self.customer, rating=5, description="b")
        self.r3 = Review.objects.create(business_user=self.business, reviewer=self.customer2, rating=3, description="c")

        self.list_url = reverse("reviews-list")

    def test_filter_by_business_user_id(self):
        self.client.login(username="cust", password="pw123456")
        res = self.client.get(self.list_url, {"business_user_id": self.business.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in res.json()}
        self.assertEqual(ids, {self.r1.id, self.r3.id})

    def test_filter_by_reviewer_id(self):
        self.client.login(username="cust", password="pw123456")
        res = self.client.get(self.list_url, {"reviewer_id": self.customer.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in res.json()}
        self.assertEqual(ids, {self.r1.id, self.r2.id})
