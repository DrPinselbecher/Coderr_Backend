from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReviewsViewSet

router = DefaultRouter()
router.register(r"", ReviewsViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
]