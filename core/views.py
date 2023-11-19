from django.shortcuts import render


def error400(request, exception):
    return render(request, "error.html", context={"code": 400}, status=404)


def error404(request, exception):
    return render(request, "error.html", context={"code": 404}, status=404)


def error500(request):
    return render(request, "error.html", context={"code": 500}, status=500)
