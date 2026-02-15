from django.contrib import admin
from .models import Order

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "customer_user", "business_user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "customer_user__username", "business_user__username")