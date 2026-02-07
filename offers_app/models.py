
from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="offers"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="offers/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class OfferDetail(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.offer.title} – {self.price}€ / {self.delivery_time_in_days} Tage"

