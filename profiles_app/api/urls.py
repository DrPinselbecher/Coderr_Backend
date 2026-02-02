from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ProfileRedirectView, BusinessProfileListView, CustomerProfileListView

router = DefaultRouter()
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
    path('', ProfileRedirectView.as_view()),
    path('', include(router.urls)),
]
