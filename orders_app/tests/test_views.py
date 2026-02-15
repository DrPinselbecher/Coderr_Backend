from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from orders_app.models import Order


class OrdersCountViewsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.other_business = User.objects.create_user(username="biz2", password="pw123456")
        Profile.objects.create(user=self.other_business, type="business")

        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="A",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="B",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="completed",
        )
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="C",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )

    def test_order_count_requires_auth(self):
        url = reverse("order-count", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_returns_in_progress_count(self):
        self.client.login(username="cust", password="pw123456")
        url = reverse("order-count", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"order_count": 2})

    def test_completed_order_count_returns_completed_count(self):
        self.client.login(username="cust", password="pw123456")
        url = reverse("completed-order-count", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"completed_order_count": 1})

    def test_order_count_404_if_user_not_business(self):
        self.client.login(username="cust", password="pw123456")
        url = reverse("order-count", args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_404_if_user_not_found(self):
        self.client.login(username="cust", password="pw123456")
        url = reverse("order-count", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
