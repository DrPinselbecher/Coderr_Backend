from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import OffersViewSet

router = DefaultRouter()
router.register(r"", OffersViewSet, basename="offers")

urlpatterns = [
    path("", include(router.urls)),
]
