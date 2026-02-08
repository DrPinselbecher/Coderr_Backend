# offers_app/api/redirects.py
from django.shortcuts import redirect

def offerdetail_redirect(request, pk):
    return redirect(f"/api/offerdetails/{pk}/", permanent=False)
