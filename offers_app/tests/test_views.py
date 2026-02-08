from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIClient
from rest_framework import status

from offers_app.models import Offer, OfferDetail


def ensure_profile(user, profile_type: str):
    Profile = apps.get_model("profiles_app", "Profile")
    profile, created = Profile.objects.get_or_create(user=user, defaults={"type": profile_type})
    if not created and getattr(profile, "type", None) != profile_type:
        profile.type = profile_type
        profile.save()
    return profile


class OfferViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.owner = User.objects.create_user(username="owner", password="pw123456")
        ensure_profile(self.owner, "business")

        self.viewer = User.objects.create_user(username="viewer", password="pw123456")
        ensure_profile(self.viewer, "customer")

        self.offer = Offer.objects.create(user=self.owner, title="A", description="B", image=None)
        OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=5,
            price="100.00", features=["A"], offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Standard", revisions=2, delivery_time_in_days=7,
            price="200.00", features=["A", "B"], offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Premium", revisions=3, delivery_time_in_days=10,
            price="500.00", features=["A", "B", "C"], offer_type="premium"
        )

    def test_retrieve_offer_requires_auth(self):
        url = f"/api/offers/{self.offer.id}/"
        res = self.client.get(url)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_retrieve_offer_authenticated_ok(self):
        url = f"/api/offers/{self.offer.id}/"
        self.client.force_authenticate(user=self.viewer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_offerdetail_endpoint_get_only_and_requires_auth(self):
        detail = OfferDetail.objects.get(offer=self.offer, offer_type="basic")
        url = f"/api/offerdetails/{detail.id}/"

        res = self.client.get(url)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        self.client.force_authenticate(user=self.viewer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(url, {"x": 1}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
