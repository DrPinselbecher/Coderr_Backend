"""
DRF router configuration for reviews endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReviewsViewSet

router = DefaultRouter()
router.register(r"", ReviewsViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
]
