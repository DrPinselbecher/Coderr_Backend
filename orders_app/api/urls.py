"""
DRF router configuration for orders endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrdersViewSet

router = DefaultRouter()
router.register(r"", OrdersViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
]
