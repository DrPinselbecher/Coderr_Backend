"""
Serializer definitions for base info stats payload.
"""

from rest_framework import serializers


class BaseInfoSerializer(serializers.Serializer):
    """
    Validates and serializes the aggregated base info response payload.
    """

    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()
