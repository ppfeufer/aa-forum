"""
Administration related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

from aa_forum.models import Boards, Categories


@login_required
@permission_required("aa_forum.manage_forum")
def admin_index(request: WSGIRequest) -> HttpResponse:

    categories = (
        Categories.objects.prefetch_related(
            Prefetch(
                "boards",
                queryset=Boards.objects.filter(parent_board__isnull=True).order_by(
                    "order"
                ),
                # to_attr="category_boards",
            )
        )
        .all()
        .order_by("order")
    )

    context = {"categories": categories}

    return render(request, "aa_forum/view/administration/index.html", context)
