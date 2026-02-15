from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from orders_app.models import Order


class OrdersPermissionsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.other_business = User.objects.create_user(username="biz2", password="pw123456")
        Profile.objects.create(user=self.other_business, type="business")

        self.order = Order.objects.create(
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

    def test_business_owner_can_patch(self):
        url = reverse("orders-detail", args=[self.order.id])
        self.client.login(username="biz", password="pw123456")
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_business_cannot_patch(self):
        url = reverse("orders-detail", args=[self.order.id])
        self.client.login(username="biz2", password="pw123456")
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
