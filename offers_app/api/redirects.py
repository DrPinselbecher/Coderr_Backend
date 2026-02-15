"""
Simple redirect helper to map legacy URLs to the API endpoint.
"""

from django.shortcuts import redirect


def offerdetail_redirect(request, pk):
    """
    Redirect to the OfferDetail API endpoint for the given primary key.

    Args:
        request: Django HttpRequest
        pk: OfferDetail primary key

    Returns:
        HttpResponseRedirect: temporary redirect (permanent=False)
    """
    return redirect(f"/api/offerdetails/{pk}/", permanent=False)
