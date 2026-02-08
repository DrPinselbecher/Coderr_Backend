from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIClient

from offers_app.models import Offer, OfferDetail


def ensure_profile(user, profile_type: str):
    Profile = apps.get_model("profiles_app", "Profile")
    profile, created = Profile.objects.get_or_create(user=user, defaults={"type": profile_type})
    if not created and getattr(profile, "type", None) != profile_type:
        profile.type = profile_type
        profile.save()
    return profile


class OfferDetailRedirectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.user = User.objects.create_user(username="u1", password="pw123456")
        ensure_profile(self.user, "customer")

        owner = User.objects.create_user(username="biz", password="pw123456")
        ensure_profile(owner, "business")

        offer = Offer.objects.create(user=owner, title="A", description="B", image=None)
        self.detail = OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price="100.00",
            features=["A"],
            offer_type="basic",
        )

    def test_offerdetails_redirects_to_api_path(self):
        # NOTE: this assumes you added the redirect URL:
        # path("offerdetails/<int:pk>/", offerdetail_redirect)
        url = f"/offerdetails/{self.detail.id}/"
        res = self.client.get(url, follow=False)
        self.assertIn(res.status_code, [301, 302, 307, 308])
        self.assertEqual(res["Location"], f"/api/offerdetails/{self.detail.id}/")
