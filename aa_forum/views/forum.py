"""
The views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


@login_required
@permission_required("aa_forum.basic_access")
def forum_index(request: WSGIRequest) -> HttpResponse:
    """
    Forum index
    :param request:
    :type request:
    """

    context = {}

    return render(request, "aa_forum/view/forum/index.html", context)
