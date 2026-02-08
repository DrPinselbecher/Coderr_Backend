# offers_app/api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import OffersViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r"", OffersViewSet, basename="offers")
router.register(r"offerdetails", OfferDetailViewSet, basename="offerdetails")

urlpatterns = [
    path("", include(router.urls)),
]
