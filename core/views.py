from django.shortcuts import render
from django.conf import settings
from threading import Lock

def error400(request, exception):
    context = {"code": 400, "message": "Bad Request"}
    return render(request, "error.html", context=context, status=404)


def error404(request, exception):
    context = {
        "code": 404,
        "message": "Page Not Found",
    }
    return render(request, "error.html", context=context, status=404)


def error500(request):
    context = {
        "code": 500,
        "message": "Internal Server Error",
    }
    return render(request, "error.html", context=context, status=500)

def initialize_scheduler():
    with initialization_lock:
        if settings.AUTO_SEND_NOTIFICAITON:
            from . import runapscheduler
            runapscheduler.start()
            initialization_lock = Lock()

