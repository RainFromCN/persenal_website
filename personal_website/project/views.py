from django.shortcuts import render
from django.http import HttpResponse, Http404
import os


from .models import Project


# Create your views here.
def index(request):
    projects = Project.objects.all()
    return render(request, "project/index.html", {'projects': projects})


def introduction(request, prj_id):
    project = Project.objects.filter(prj_id=prj_id)[0]
    return render(request, "project/introduction.html", {'project': project})


def paper(request, prj_id):
    project = Project.objects.filter(prj_id=prj_id)[0]
    return render(request, "project/paper.html", {'project': project})


def tutorial(request, prj_id):
    project = Project.objects.filter(prj_id=prj_id)[0]
    return render(request, "project/tutorial.html", {'project': project})


def image(request, prj_id: int, filename: str):
    path = os.path.join(os.path.dirname(__file__), 'static', 'project', 'image')
    path = os.path.join(path, f"{prj_id}", filename)
    image_type = None
    if '.png' in filename: image_type = 'png'
    if '.jpg' in filename: image_type = 'jpg'

    if os.path.isfile(path) and image_type:
        data = open(path, 'rb').read()
        return HttpResponse(data, content_type=f"image/{image_type}")
    else:
        return Http404(f"Image {filename} not found!")
