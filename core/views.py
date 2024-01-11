from django.shortcuts import render
from django.conf import settings


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

    # if settings.SETTINGS_MODULE == "cole_rochman.settings.dev":


# from . import runapscheduler

# print("debug:: runapscheduler")
# runapscheduler.start()  # 수동알림 모드
