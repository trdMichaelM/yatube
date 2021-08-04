from http import HTTPStatus

from django.views.decorators.http import require_GET
from django.shortcuts import render


@require_GET
def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=HTTPStatus.NOT_FOUND
    )


@require_GET
def server_error(request):
    return render(
        request,
        "misc/500.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
