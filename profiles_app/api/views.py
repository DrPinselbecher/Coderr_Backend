"""
Views for profile endpoints:
- ProfileViewSet: exposes a single "my profile" via list() and user_id lookup
- ProfileRedirectView: redirects /api/profile/ -> /api/profile/<user_id>/
- BusinessProfileListView: lists all business profiles
- CustomerProfileListView: lists all customer profiles
"""

from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.models import Profile
from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer, ProfileSummarySerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Profile ViewSet.

    Notes:
        - lookup_field is user_id, so detail routes look like /<user_id>/
        - list() is overridden to return the current user's profile as single object
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = "user_id"

    def list(self, request, *args, **kwargs):
        """
        Return the authenticated user's profile as a single object.
        """
        profile = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class ProfileRedirectView(APIView):
    """
    Redirect /api/profile/ to /api/profile/<user_id>/ for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        return redirect(f"{profile.user.id}/")


class BusinessProfileListView(generics.ListAPIView):
    """
    List all business profiles.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSummarySerializer

    def get_queryset(self):
        return (
            Profile.objects.select_related("user")
            .filter(type="business")
            .order_by("user__username")
        )


class CustomerProfileListView(generics.ListAPIView):
    """
    List all customer profiles.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSummarySerializer

    def get_queryset(self):
        return (
            Profile.objects.select_related("user")
            .filter(type="customer")
            .order_by("user__username")
        )
