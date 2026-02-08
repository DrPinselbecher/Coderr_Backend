from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIRequestFactory

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import (
    OfferCreateSerializer,
    OfferPatchSerializer,
    OfferRetrieveSerializer,
)


def ensure_profile(user, profile_type: str):
    Profile = apps.get_model("profiles_app", "Profile")
    profile, created = Profile.objects.get_or_create(user=user, defaults={"type": profile_type})
    if not created and getattr(profile, "type", None) != profile_type:
        profile.type = profile_type
        profile.save()
    return profile


class OfferSerializersTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        User = get_user_model()

        self.business_owner = User.objects.create_user(username="biz", password="pw123456")
        ensure_profile(self.business_owner, "business")

        self.offer = Offer.objects.create(user=self.business_owner, title="Offer", description="Desc", image=None)
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

    def test_offer_create_serializer_requires_exactly_3_details(self):
        req = self.factory.post("/api/offers/")
        req.user = self.business_owner

        payload = {
            "title": "X",
            "image": None,
            "description": "Y",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                }
            ],
        }

        s = OfferCreateSerializer(data=payload, context={"request": req})
        self.assertFalse(s.is_valid())
        self.assertIn("details", s.errors)

    def test_offer_create_serializer_requires_basic_standard_premium(self):
        req = self.factory.post("/api/offers/")
        req.user = self.business_owner

        payload = {
            "title": "X",
            "image": None,
            "description": "Y",
            "details": [
                {
                    "title": "A",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [],
                    "offer_type": "basic",
                },
                {
                    "title": "B",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [],
                    "offer_type": "basic",  # duplicate
                },
                {
                    "title": "C",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [],
                    "offer_type": "premium",
                },
            ],
        }

        s = OfferCreateSerializer(data=payload, context={"request": req})
        self.assertFalse(s.is_valid())
        self.assertIn("details", s.errors)

    def test_offer_patch_serializer_updates_only_sent_fields_and_details_by_type(self):
        payload = {
            "title": "Updated Title",
            "details": [{"offer_type": "basic", "price": "123.00"}],
        }

        s = OfferPatchSerializer(instance=self.offer, data=payload, partial=True)
        self.assertTrue(s.is_valid(), s.errors)

        updated = s.save()

        self.assertEqual(updated.title, "Updated Title")

        basic = OfferDetail.objects.get(offer=updated, offer_type="basic")
        standard = OfferDetail.objects.get(offer=updated, offer_type="standard")

        self.assertEqual(str(basic.price), "123.00")
        self.assertEqual(str(standard.price), "200.00")  # unchanged

    def test_offer_patch_serializer_rejects_duplicate_offer_type_in_payload(self):
        payload = {
            "details": [
                {"offer_type": "basic", "price": "110.00"},
                {"offer_type": "basic", "price": "120.00"},
            ]
        }
        s = OfferPatchSerializer(instance=self.offer, data=payload, partial=True)
        self.assertFalse(s.is_valid())
        self.assertIn("details", s.errors)

    def test_offer_retrieve_serializer_builds_absolute_detail_urls(self):
        req = self.factory.get("/api/offers/1/")
        req.user = self.business_owner
        req.META["HTTP_HOST"] = "testserver"

        s = OfferRetrieveSerializer(instance=self.offer, context={"request": req})
        data = s.data

        self.assertEqual(data["id"], self.offer.id)
        self.assertIn("details", data)
        self.assertEqual(len(data["details"]), 3)

        for d in data["details"]:
            self.assertIn("url", d)
            self.assertTrue(d["url"].startswith("http://testserver/"))
            self.assertIn("/api/offerdetails/", d["url"])
