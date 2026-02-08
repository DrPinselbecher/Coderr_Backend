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


def make_offer(owner, title, desc, prices, delivery):
    offer = Offer.objects.create(user=owner, title=title, description=desc, image=None)
    OfferDetail.objects.create(
        offer=offer, title="Basic", revisions=1, delivery_time_in_days=delivery[0],
        price=prices[0], features=["A"], offer_type="basic"
    )
    OfferDetail.objects.create(
        offer=offer, title="Standard", revisions=2, delivery_time_in_days=delivery[1],
        price=prices[1], features=["A", "B"], offer_type="standard"
    )
    OfferDetail.objects.create(
        offer=offer, title="Premium", revisions=3, delivery_time_in_days=delivery[2],
        price=prices[2], features=["A", "B", "C"], offer_type="premium"
    )
    return offer


class OfferSearchFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.biz1 = User.objects.create_user(username="biz1", password="pw123456")
        ensure_profile(self.biz1, "business")

        self.biz2 = User.objects.create_user(username="biz2", password="pw123456")
        ensure_profile(self.biz2, "business")

        make_offer(self.biz1, "Website Design", "Professionelles Website-Design", prices=(100, 200, 500), delivery=(7, 10, 14))
        make_offer(self.biz1, "Logo Paket", "Logo und Brand", prices=(50, 120, 300), delivery=(5, 7, 10))
        make_offer(self.biz2, "SEO Paket", "Suchmaschinen Optimierung", prices=(80, 160, 400), delivery=(3, 5, 7))

    def test_filter_creator_id(self):
        url = f"/api/offers/?creator_id={self.biz2.id}"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["user"], self.biz2.id)

    def test_filter_min_price(self):
        url = "/api/offers/?min_price=80"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data["count"], 2)

        for item in res.data["results"]:
            self.assertGreaterEqual(float(item["min_price"]), 80.0)

    def test_filter_max_delivery_time(self):
        url = "/api/offers/?max_delivery_time=5"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for item in res.data["results"]:
            self.assertLessEqual(int(item["min_delivery_time"]), 5)

    def test_search_title_description(self):
        url = "/api/offers/?search=website"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertIn("Website", res.data["results"][0]["title"])

    def test_ordering_min_price(self):
        url = "/api/offers/?ordering=min_price"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        prices = [float(item["min_price"]) for item in res.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_pagination_page_size(self):
        url = "/api/offers/?page_size=2"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
