from django.http import HttpResponse
from django.template import loader
from .forms import NameForm


def index(request):
    template = loader.get_template("index.html")
    form = NameForm()
    context = {
        "title": "ok",
        "form": form
    }

    return HttpResponse(template.render(context, request))
