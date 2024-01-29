from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("index.html")
    context = {
        "title": "ok"
    }
    return HttpResponse(template.render(context, request))
