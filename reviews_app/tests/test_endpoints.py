from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewsEndpointsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.customer2 = User.objects.create_user(username="cust2", password="pw123456")
        Profile.objects.create(user=self.customer2, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.business2 = User.objects.create_user(username="biz2", password="pw123456")
        Profile.objects.create(user=self.business2, type="business")

        self.list_url = reverse("reviews-list")

    def test_reviews_list_requires_auth(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reviews_list_returns_200_for_authenticated(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        self.client.login(username="cust", password="pw123456")
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.json(), list)

    def test_reviews_post_requires_auth(self):
        res = self.client.post(
            self.list_url,
            data={"business_user": self.business.id, "rating": 4, "description": "x"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reviews_post_requires_customer_profile(self):
        self.client.login(username="biz", password="pw123456")
        res = self.client.post(
            self.list_url,
            data={"business_user": self.business.id, "rating": 4, "description": "x"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews_post_creates_review(self):
        self.client.login(username="cust", password="pw123456")
        res = self.client.post(
            self.list_url,
            data={"business_user": self.business.id, "rating": 4, "description": "Alles war toll!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["business_user"], self.business.id)
        self.assertEqual(data["reviewer"], self.customer.id)
        self.assertEqual(data["rating"], 4)
        self.assertEqual(data["description"], "Alles war toll!")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_reviews_post_duplicate_returns_400(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")

        self.client.login(username="cust", password="pw123456")
        res = self.client.post(
            self.list_url,
            data={"business_user": self.business.id, "rating": 5, "description": "again"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviews_post_rejects_non_business_target(self):
        self.client.login(username="cust", password="pw123456")
        res = self.client.post(
            self.list_url,
            data={"business_user": self.customer2.id, "rating": 4, "description": "x"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviews_patch_requires_auth(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])
        res = self.client.patch(url, data={"rating": 5}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reviews_patch_requires_owner(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])

        self.client.login(username="cust2", password="pw123456")
        res = self.client.patch(url, data={"rating": 5}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews_patch_only_allows_rating_and_description(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])

        self.client.login(username="cust", password="pw123456")
        res = self.client.patch(url, data={"rating": 5, "business_user": self.business2.id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviews_patch_updates_review(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        old_updated = r.updated_at
        url = reverse("reviews-detail", args=[r.id])

        self.client.login(username="cust", password="pw123456")
        res = self.client.patch(url, data={"rating": 5, "description": "Noch besser!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        r.refresh_from_db()
        self.assertEqual(r.rating, 5)
        self.assertEqual(r.description, "Noch besser!")
        self.assertNotEqual(r.updated_at, old_updated)

        data = res.json()
        self.assertEqual(data["rating"], 5)
        self.assertEqual(data["description"], "Noch besser!")
        self.assertIn("updated_at", data)

    def test_reviews_delete_requires_auth(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reviews_delete_requires_owner(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])

        self.client.login(username="cust2", password="pw123456")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews_delete_owner_ok(self):
        r = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        url = reverse("reviews-detail", args=[r.id])

        self.client.login(username="cust", password="pw123456")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=r.id).exists())
