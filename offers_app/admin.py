from django.contrib import admin

# Register your models here.
from .models import Offer, OfferDetail

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    search_fields = ("title", "description", "user__username")
    list_filter = ("created_at",)