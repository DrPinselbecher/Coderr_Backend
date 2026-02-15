"""
URL routing for the base info endpoint.
"""

from django.urls import path

from .views import BaseInfoView

urlpatterns = [
    path("", BaseInfoView.as_view(), name="base-info"),
]
