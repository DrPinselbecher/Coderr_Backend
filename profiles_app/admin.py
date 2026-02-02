from django.contrib import admin
from profiles_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "created_at")
    list_select_related = ("user",)

    fields = (
        "user",
        "type",
        "file",
        "location",
        "tel",
        "description",
        "working_hours",
        "created_at",
    )
    readonly_fields = ("created_at",)
