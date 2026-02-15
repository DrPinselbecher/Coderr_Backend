"""
Public endpoint to deliver aggregated "base info" stats used on landing pages
or dashboards (e.g., total reviews, average rating, number of business profiles,
and total offers).
"""

from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review
from .serializers import BaseInfoSerializer


class BaseInfoView(APIView):
    """
    Return aggregated platform statistics.

    Authentication:
        - Public endpoint (AllowAny)

    Response schema:
        - review_count: int
        - average_rating: float (1 decimal)
        - business_profile_count: int
        - offer_count: int
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Get aggregated base info statistics.

        Returns:
            Response: Serialized BaseInfo payload.
        """
        review_count = Review.objects.count()

        avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        average_rating = round(float(avg_rating), 1) if avg_rating is not None else 0.0

        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()

        payload = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        serializer = BaseInfoSerializer(payload)
        return Response(serializer.data)
