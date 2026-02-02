from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from profiles_app.models import Profile
from .serializers import ProfileSerializer, ProfileSummarySerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect, get_object_or_404


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = "user_id"

    def list(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    

class ProfileRedirectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        return redirect(f"{profile.user.id}/")
    

class BusinessProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSummarySerializer

    def get_queryset(self):
        return (
            Profile.objects
            .select_related("user")
            .filter(type="business")
            .order_by("user__username")
        )
    
class CustomerProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSummarySerializer

    def get_queryset(self):
        return (
            Profile.objects
            .select_related("user")
            .filter(type="customer")
            .order_by("user__username")
        )