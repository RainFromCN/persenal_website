from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, StreamingHttpResponse
from .models import User
import os


from .models import Project, User, Purchase


def read_file(file_name, chunk_size=512):
    with open(file_name, "rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


# Create your views here.
def index(request):
    projects = Project.objects.all()
    for project in projects:
        project.lock = True if project.price > 0 else False
    context = {'projects': projects}
    if 'username' in request.session:
        context['username'] = request.session['username']
    return render(request, "project/index.html", context)


# def tutorial(request, prj_id, chapter_id):
#     project = Project.objects.filter(prj_id=prj_id)[0]
#     project.visit_tutorial += 1
#     project.save()
#     chapters = project.tutorial.split("<h2>")
#     if len(chapters[0]) == 0:
#         del chapters[0]
#     num_chapters = list(range(1, len(chapters) + 1))
#     chapter = chapters[chapter_id - 1]

#     context = {'chapter': f"<h2>{chapter}", 'num_chapters': num_chapters, 'project': project}
#     if len(chapters) > chapter_id:
#         context['next_chapter_id'] = chapter_id + 1
    
#     return render(request, "project/tutorial.html", context)


# def code(request, prj_id):
#     project = Project.objects.filter(prj_id=prj_id)[0]
#     project.visit_code += 1
#     project.save()

#     path = os.path.join(os.path.dirname(__file__), 'static', 'project', 'code')
#     path = os.path.join(path, f"project{prj_id}.zip")

#     if os.path.exists(path):
#         response = StreamingHttpResponse(read_file(path))
#         response['Content-Type'] = "application/octet-stream"
#         response['Content-Disposition'] = f'attachment; filename=project{prj_id}.zip'
#         return response
#     else:
#         return Http404("code is not exist.")


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


def signup(request):
    if request.method == "POST":
        username = request.POST["user_name"]
        password = request.POST["user_pw"]
        cond1 = len(username) < 20 and len(username) > 0
        cond2 = len(password) < 20 and len(password) > 0
        cond3 = len(User.objects.filter(name=username)) == 0

        if not cond1 or not cond2:
            return render(request, "project/signup.html", {'message': '用户名和密码都应小于20个字符且非空'})
        if not cond3:
            return render(request, "project/signup.html", {'message': '用户名已被注册'})
        
        user = User(name=username, password=password)
        user.save()

        return render(request, "project/signup.html", {'message': '注册成功',
                                                       'success': '1'})

    elif request.method == 'GET':
        return render(request, "project/signup.html", {})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.filter(name=username)
        if user.count() == 0:
            return render(request, "project/login.html", {'message': '用户名不存在'})
        
        user = user[0]
        if user.password != password:
            return render(request, "project/login.html", {'message': '密码错误'})
        
        user.login_times += 1
        user.save()
        request.session['username'] = user.name

        return redirect(reverse('project:index'))
    else:
        return render(request, "project/login.html", {})


def exit(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect(reverse('project:index'))


def detail(request, prj_id, page):
    project = Project.objects.filter(prj_id=prj_id).first()
    context = {'project': project}
    if 'username' in request.session:
        context['username'] = request.session['username']        
        if Purchase.objects.filter(user__name=context['username'], project__prj_id=prj_id).count():
            context['own'] = True
    context[f'page{page}'] = True
    return render(request, "project/detail.html", context)
