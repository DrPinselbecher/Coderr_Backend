from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIClient
from rest_framework import status

from offers_app.models import Offer, OfferDetail


def ensure_profile(user, profile_type: str):
    """
    Creates/updates a profile for the user with given type.
    Assumes a profiles_app.Profile model exists with fields: user (OneToOne/ForeignKey) and type.
    """
    Profile = apps.get_model("profiles_app", "Profile")
    profile, created = Profile.objects.get_or_create(user=user, defaults={"type": profile_type})
    if not created and getattr(profile, "type", None) != profile_type:
        profile.type = profile_type
        profile.save()
    return profile


def make_offer(owner, title="Offer 1", desc="Desc", prices=(100, 200, 500), delivery=(5, 7, 10)):
    offer = Offer.objects.create(user=owner, title=title, description=desc, image=None)

    OfferDetail.objects.create(
        offer=offer,
        title="Basic",
        revisions=1,
        delivery_time_in_days=delivery[0],
        price=prices[0],
        features=["A"],
        offer_type="basic",
    )
    OfferDetail.objects.create(
        offer=offer,
        title="Standard",
        revisions=2,
        delivery_time_in_days=delivery[1],
        price=prices[1],
        features=["A", "B"],
        offer_type="standard",
    )
    OfferDetail.objects.create(
        offer=offer,
        title="Premium",
        revisions=3,
        delivery_time_in_days=delivery[2],
        price=prices[2],
        features=["A", "B", "C"],
        offer_type="premium",
    )
    return offer


class OfferEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.business_owner = User.objects.create_user(username="business_owner", password="pw123456")
        ensure_profile(self.business_owner, "business")

        self.customer_user = User.objects.create_user(username="customer_user", password="pw123456")
        ensure_profile(self.customer_user, "customer")

        self.other_business = User.objects.create_user(username="other_business", password="pw123456")
        ensure_profile(self.other_business, "business")

        self.offer = make_offer(self.business_owner, title="Grafikdesign-Paket", desc="Ein Paket")

    def test_get_offers_list_is_public(self):
        url = "/api/offers/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)

    def test_post_offers_requires_auth(self):
        url = "/api/offers/"
        payload = {
            "title": "New Offer",
            "image": None,
            "description": "Desc",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["X"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["X", "Y"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["X", "Y", "Z"],
                    "offer_type": "premium",
                },
            ],
        }
        res = self.client.post(url, payload, format="json")
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_post_offers_requires_business_user(self):
        url = "/api/offers/"
        payload = {
            "title": "New Offer",
            "image": None,
            "description": "Desc",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["X"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["X", "Y"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["X", "Y", "Z"],
                    "offer_type": "premium",
                },
            ],
        }

        self.client.force_authenticate(user=self.customer_user)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_offers_success_returns_offer_and_detail_ids(self):
        url = "/api/offers/"
        payload = {
            "title": "Grafikdesign-Paket ULTIMATE",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium",
                },
            ],
        }

        self.client.force_authenticate(user=self.business_owner)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertIn("id", res.data)
        self.assertEqual(res.data["title"], payload["title"])
        self.assertEqual(len(res.data["details"]), 3)
        self.assertTrue(all("id" in d for d in res.data["details"]))

    def test_get_offer_retrieve_requires_auth(self):
        url = f"/api/offers/{self.offer.id}/"
        res = self.client.get(url)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_get_offer_retrieve_success_shape(self):
        url = f"/api/offers/{self.offer.id}/"
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["id"], self.offer.id)
        self.assertEqual(res.data["user"], self.business_owner.id)
        self.assertIn("details", res.data)
        self.assertEqual(len(res.data["details"]), 3)
        self.assertIn("min_price", res.data)
        self.assertIn("min_delivery_time", res.data)

        for item in res.data["details"]:
            self.assertIn("id", item)
            self.assertIn("url", item)
            self.assertIn("/api/offerdetails/", item["url"])

    def test_patch_offer_requires_owner(self):
        url = f"/api/offers/{self.offer.id}/"
        payload = {"title": "Updated"}

        self.client.force_authenticate(user=self.other_business)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_owner_success_and_details_update_by_type(self):
        url = f"/api/offers/{self.offer.id}/"

        basic_before = OfferDetail.objects.get(offer=self.offer, offer_type="basic")
        standard_before = OfferDetail.objects.get(offer=self.offer, offer_type="standard")

        payload = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "offer_type": "basic",
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": "120.00",
                    "features": ["Logo Design", "Flyer"],
                }
            ],
        }

        self.client.force_authenticate(user=self.business_owner)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated Grafikdesign-Paket")

        basic_after = OfferDetail.objects.get(offer=self.offer, offer_type="basic")
        standard_after = OfferDetail.objects.get(offer=self.offer, offer_type="standard")

        self.assertEqual(basic_after.id, basic_before.id)
        self.assertEqual(standard_after.id, standard_before.id)

        self.assertEqual(basic_after.title, "Basic Design Updated")
        self.assertEqual(basic_after.revisions, 3)
        self.assertEqual(basic_after.delivery_time_in_days, 6)
        self.assertEqual(str(basic_after.price), "120.00")
        self.assertEqual(basic_after.features, ["Logo Design", "Flyer"])

    def test_delete_offer_requires_owner(self):
        url = f"/api/offers/{self.offer.id}/"

        self.client.force_authenticate(user=self.other_business)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_owner_success_204(self):
        url = f"/api/offers/{self.offer.id}/"

        self.client.force_authenticate(user=self.business_owner)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())
        self.assertEqual(OfferDetail.objects.filter(offer_id=self.offer.id).count(), 0)
