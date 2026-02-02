from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ProfileRedirectView, BusinessProfileListView

router = DefaultRouter()
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('', ProfileRedirectView.as_view()),
    path('', include(router.urls)),
]
