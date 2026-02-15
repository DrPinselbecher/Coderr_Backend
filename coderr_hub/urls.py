from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from offers_app.api.views import OfferDetailViewSet
from offers_app.api.redirects import offerdetail_redirect

from orders_app.api.views import OrderCountView, CompletedOrderCountView


urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),

    path("api/", include("user_auth_app.api.urls")),
    path("api/profile/", include("profiles_app.api.urls")),
    path("api/profiles/", include("profiles_app.api.urls")),

    path("api/offers/", include("offers_app.api.urls")),
    path("api/offerdetails/<int:pk>/", OfferDetailViewSet.as_view({"get": "retrieve"})),
    path("offerdetails/<int:pk>/", offerdetail_redirect),

    path("api/orders/", include("orders_app.api.urls")),
    path("api/order-count/<int:business_user_id>/", OrderCountView.as_view(), name="order-count"),
    path("api/completed-order-count/<int:business_user_id>/", CompletedOrderCountView.as_view(), name="completed-order-count"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
