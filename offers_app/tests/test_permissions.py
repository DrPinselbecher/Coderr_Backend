from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIRequestFactory

from offers_app.models import Offer
from offers_app.api.permissions import IsBusinessUser, IsOfferOwner


def ensure_profile(user, profile_type: str):
    Profile = apps.get_model("profiles_app", "Profile")
    profile, created = Profile.objects.get_or_create(user=user, defaults={"type": profile_type})
    if not created and getattr(profile, "type", None) != profile_type:
        profile.type = profile_type
        profile.save()
    return profile


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        User = get_user_model()

        self.business = User.objects.create_user(username="biz", password="pw123456")
        ensure_profile(self.business, "business")

        self.customer = User.objects.create_user(username="cust", password="pw123456")
        ensure_profile(self.customer, "customer")

        self.offer = Offer.objects.create(user=self.business, title="A", description="B", image=None)

    def test_is_business_user(self):
        req = self.factory.post("/api/offers/")
        req.user = self.business
        self.assertTrue(IsBusinessUser().has_permission(req, view=None))

        req.user = self.customer
        self.assertFalse(IsBusinessUser().has_permission(req, view=None))

    def test_is_offer_owner_get_requires_auth(self):
        req = self.factory.get("/api/offers/1/")
        req.user = self.business
        self.assertTrue(IsOfferOwner().has_object_permission(req, view=None, obj=self.offer))

        req.user = self.customer
        self.assertTrue(IsOfferOwner().has_object_permission(req, view=None, obj=self.offer))

        req.user = type("Anon", (), {"is_authenticated": False})()
        self.assertFalse(IsOfferOwner().has_object_permission(req, view=None, obj=self.offer))

    def test_is_offer_owner_patch_requires_owner(self):
        req = self.factory.patch("/api/offers/1/")
        req.user = self.business
        self.assertTrue(IsOfferOwner().has_object_permission(req, view=None, obj=self.offer))

        req.user = self.customer
        self.assertFalse(IsOfferOwner().has_object_permission(req, view=None, obj=self.offer))
