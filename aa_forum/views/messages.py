"""
Messages views
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def index(request: WSGIRequest) -> HttpResponse:
    """
    Messages overview
    :return:
    """

    context = {}

    return render(request, "aa_forum/view/messages/index.html", context)
