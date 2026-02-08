from django.conf import settings
from django.db import models


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offers/", null=True, blank=True)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )

    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    features = models.JSONField(default=list, blank=True)

    offer_type = models.CharField(
        max_length=20,
        choices=OFFER_TYPE_CHOICES,
    )

    def __str__(self):
        return f"{self.offer.title} – {self.offer_type}"
