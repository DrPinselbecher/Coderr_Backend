from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewsPermissionsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.other_customer = User.objects.create_user(username="cust2", password="pw123456")
        Profile.objects.create(user=self.other_customer, type="customer")

        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="ok",
        )

    def test_only_owner_can_patch(self):
        url = reverse("reviews-detail", args=[self.review.id])

        self.client.login(username="cust2", password="pw123456")
        res = self.client.patch(url, data={"rating": 5}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username="cust", password="pw123456")
        res = self.client.patch(url, data={"rating": 5}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_only_owner_can_delete(self):
        url = reverse("reviews-detail", args=[self.review.id])

        self.client.login(username="cust2", password="pw123456")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username="cust", password="pw123456")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
