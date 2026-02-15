from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from reviews_app.models import Review
from .filters import ReviewFilter
from .permissions import IsCustomerUser, IsReviewOwner
from .serializers import (
    ReviewCreateSerializer,
    ReviewDetailSerializer,
    ReviewListSerializer,
    ReviewPatchSerializer,
)


class ReviewsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["updated_at", "rating"]

    def get_permissions(self):
        permissions = super().get_permissions()

        if self.action == "create":
            permissions.append(IsCustomerUser())
        if self.action in ["partial_update", "destroy"]:
            permissions.append(IsReviewOwner())
        return permissions

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        if self.action == "partial_update":
            return ReviewPatchSerializer
        if self.action == "list":
            return ReviewListSerializer
        return ReviewDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        return Response(
            ReviewDetailSerializer(review, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        allowed_keys = {"rating", "description"}
        extra_keys = set(request.data.keys()) - allowed_keys
        if extra_keys:
            return Response(
                {"detail": "Unallowed fields in request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = self.get_object()

        serializer = ReviewPatchSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        review.refresh_from_db(fields=["updated_at", "rating", "description"])

        return Response(
            ReviewDetailSerializer(review, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
