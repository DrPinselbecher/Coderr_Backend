from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrdersEndpointsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pw123456")
        Profile.objects.create(user=self.customer, type="customer")

        self.business = User.objects.create_user(username="biz", password="pw123456")
        Profile.objects.create(user=self.business, type="business")

        self.other = User.objects.create_user(username="other", password="pw123456")
        Profile.objects.create(user=self.other, type="customer")

        self.offer = Offer.objects.create(user=self.business, title="Logo", description="desc")
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )

        self.orders_list_url = reverse("orders-list")

    def test_orders_list_requires_auth(self):
        response = self.client.get(self.orders_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orders_list_returns_only_related_orders(self):
        o1 = Order.objects.create(
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
            customer_user=self.other,
            business_user=self.business,
            title="B",
            revisions=1,
            delivery_time_in_days=1,
            price="10.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )

        self.client.login(username="cust", password="pw123456")
        response = self.client.get(self.orders_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.json()]
        self.assertIn(o1.id, ids)
        self.assertEqual(len(ids), 1)

    def test_orders_post_requires_auth(self):
        response = self.client.post(self.orders_list_url, data={"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orders_post_requires_customer_type(self):
        self.client.login(username="biz", password="pw123456")
        response = self.client.post(self.orders_list_url, data={"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_post_creates_order_from_offer_detail(self):
        self.client.login(username="cust", password="pw123456")
        response = self.client.post(self.orders_list_url, data={"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data["customer_user"], self.customer.id)
        self.assertEqual(data["business_user"], self.business.id)
        self.assertEqual(data["title"], "Logo Design")
        self.assertEqual(data["revisions"], 3)
        self.assertEqual(data["delivery_time_in_days"], 5)
        self.assertEqual(str(data["price"]), "150.00")
        self.assertEqual(data["features"], ["Logo Design", "Visitenkarten"])
        self.assertEqual(data["offer_type"], "basic")
        self.assertEqual(data["status"], "in_progress")
        self.assertIn("created_at", data)

    def test_orders_post_missing_offer_detail_id(self):
        self.client.login(username="cust", password="pw123456")
        response = self.client.post(self.orders_list_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_orders_post_offer_detail_not_found(self):
        self.client.login(username="cust", password="pw123456")
        response = self.client.post(self.orders_list_url, data={"offer_detail_id": 999999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_orders_patch_requires_auth(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orders_patch_requires_business_type(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="cust", password="pw123456")
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_patch_requires_business_owner(self):
        other_biz = User.objects.create_user(username="biz2", password="pw123456")
        Profile.objects.create(user=other_biz, type="business")

        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="biz2", password="pw123456")
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_patch_rejects_unallowed_fields(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="biz", password="pw123456")
        response = self.client.patch(url, data={"status": "completed", "price": "999.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_orders_patch_updates_status(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="biz", password="pw123456")
        response = self.client.patch(url, data={"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "completed")

    def test_orders_patch_rejects_invalid_status(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="biz", password="pw123456")
        response = self.client.patch(url, data={"status": "nope"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_orders_delete_requires_auth(self):
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
        url = reverse("orders-detail", args=[order.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orders_delete_requires_staff(self):
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
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="cust", password="pw123456")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_delete_staff_ok(self):
        staff = User.objects.create_user(username="staff", password="pw123456", is_staff=True)
        Profile.objects.create(user=staff, type="customer")

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
        url = reverse("orders-detail", args=[order.id])

        self.client.login(username="staff", password="pw123456")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
