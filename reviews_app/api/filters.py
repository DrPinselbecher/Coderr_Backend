"""
django-filter FilterSet for the reviews list endpoint.
Supports filtering by business user and reviewer.
"""

import django_filters

from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """
    Filter configuration for Review queryset.

    Query params:
        - business_user_id: int
        - reviewer_id: int
    """

    business_user_id = django_filters.NumberFilter(field_name="business_user_id")
    reviewer_id = django_filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]
