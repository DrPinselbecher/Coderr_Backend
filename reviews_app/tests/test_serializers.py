from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from profiles_app.models import Profile
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewCreateSerializer, ReviewPatchSerializer


class ReviewsSerializersTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

    def test_create_serializer_valid(self):
        req = self.factory.post("/api/reviews/", {})
        req.user = self.customer
        serializer = ReviewCreateSerializer(
            data={"business_user": self.business.id, "rating": 4, "description": "ok"},
            context={"request": req},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_rejects_rating_out_of_range(self):
        req = self.factory.post("/api/reviews/", {})
        req.user = self.customer
        serializer = ReviewCreateSerializer(
            data={"business_user": self.business.id, "rating": 10, "description": "ok"},
            context={"request": req},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_create_serializer_rejects_duplicate_as_400(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")

        req = self.factory.post("/api/reviews/", {})
        req.user = self.customer
        serializer = ReviewCreateSerializer(
            data={"business_user": self.business.id, "rating": 5, "description": "again"},
            context={"request": req},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)

    def test_patch_serializer_allows_rating_and_description(self):
        review = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        serializer = ReviewPatchSerializer(review, data={"rating": 5, "description": "x"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_patch_serializer_rejects_invalid_rating(self):
        review = Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="ok")
        serializer = ReviewPatchSerializer(review, data={"rating": 0}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)
