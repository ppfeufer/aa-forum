"""
Administration related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


@login_required
@permission_required("aa_forum.manage_forum")
def admin_index(request: WSGIRequest) -> HttpResponse:

    context = {}

    return render(request, "aa_forum/view/administration/index.html", context)
