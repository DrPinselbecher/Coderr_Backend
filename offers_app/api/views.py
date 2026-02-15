"""
ViewSets for offers and offer details.

OffersViewSet:
- list: public (AllowAny)
- retrieve: authenticated
- create: authenticated + business profile
- partial_update/update/destroy: authenticated + offer owner

OfferDetailViewSet:
- read-only, authenticated
"""

from django.db.models import DecimalField, IntegerField, Min
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from offers_app.models import Offer, OfferDetail
from .filters import OfferFilter
from .pagination import OffersPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateSerializer,
    OfferDetailResponseSerializer,
    OfferListSerializer,
    OfferPatchSerializer,
    OfferResponseSerializer,
    OfferRetrieveSerializer,
)


class OffersViewSet(viewsets.ModelViewSet):
    """
    Offer CRUD endpoint with filtering/search/ordering and annotated aggregates.
    """

    pagination_class = OffersPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """
        Build queryset with optimized relations and (for list/retrieve) annotate:
        - min_price
        - min_delivery_time
        """
        querryset = Offer.objects.select_related("user").prefetch_related("details")

        if self.action in ["list", "retrieve"]:
            querryset = querryset.annotate(
                min_price=Coalesce(
                    Min("details__price"),
                    0,
                    output_field=DecimalField(max_digits=7, decimal_places=2),
                ),
                min_delivery_time=Coalesce(
                    Min("details__delivery_time_in_days"),
                    0,
                    output_field=IntegerField(),
                ),
            )
        return querryset

    def get_serializer_class(self):
        """
        Pick serializer by action.
        """
        if self.action == "create":
            return OfferCreateSerializer
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        if self.action in ["partial_update", "update"]:
            return OfferPatchSerializer
        return OfferListSerializer

    def get_permissions(self):
        """
        Pick permissions by action.
        """
        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action == "retrieve":
            return [IsAuthenticated()]
        if self.action in ["partial_update", "update", "destroy"]:
            return [IsAuthenticated(), IsOfferOwner()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Create an offer (business users only) and return normalized response.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        return Response(
            OfferResponseSerializer(offer, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an offer and optional nested details patch list.
        """
        offer = self.get_object()
        serializer = self.get_serializer(
            offer, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        return Response(
            OfferResponseSerializer(offer, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to OfferDetail resources.
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailResponseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
