"""
django-filter FilterSet for the offers list endpoint.
Supports filtering by creator, minimum price, and maximum delivery time.
"""

import django_filters

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """
    Filter configuration for Offer queryset.

    Query params:
        - creator_id: int (maps to Offer.user_id)
        - min_price: decimal (gte on annotated/field min_price)
        - max_delivery_time: int (lte on annotated/field min_delivery_time)
    """

    creator_id = django_filters.NumberFilter(field_name="user_id")
    min_price = django_filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = django_filters.NumberFilter(
        field_name="min_delivery_time", lookup_expr="lte"
    )

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]
