"""
Routes for profile endpoints:
- /business/ : list business profiles
- /customer/ : list customer profiles
- /          : redirect to /<user_id>/ of current user
- /<user_id>/ : profile viewset (lookup by user_id)
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    ProfileRedirectView,
    ProfileViewSet,
)

router = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")

urlpatterns = [
    path("business/", BusinessProfileListView.as_view(), name="business-profile-list"),
    path("customer/", CustomerProfileListView.as_view(), name="customer-profile-list"),
    path("", ProfileRedirectView.as_view(), name="profile-redirect"),
    path("", include(router.urls)),
]
