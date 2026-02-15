from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.api.serializers import OrderCreateSerializer, OrderStatusPatchSerializer
from orders_app.models import Order


class OrdersSerializersTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.offer = Offer.objects.create(user=self.business, title="Logo", description="desc")
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=["A", "B"],
            offer_type="basic",
        )

    def test_order_create_serializer_requires_offer_detail_id(self):
        serializer = OrderCreateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("offer_detail_id", serializer.errors)

    def test_order_status_patch_accepts_valid_status(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="X",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        serializer = OrderStatusPatchSerializer(order, data={"status": "completed"}, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_order_status_patch_rejects_invalid_status(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="X",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        serializer = OrderStatusPatchSerializer(order, data={"status": "invalid"}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
