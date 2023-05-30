from django.shortcuts import render


from .models import Blog, User

# Create your views here.
def index(request):
    context = {}
    key = lambda x: x.priority
    context["blogs"] = sorted(Blog.objects.all(), key=key)
    for blog in context["blogs"]:
        blog.author = User.objects.filter(user_id=blog.author_id)[0]
    return render(request, "blog/index.html", context)


def detail(request, blog_id):
    context = {}
    context['blog'] = Blog.objects.filter(blog_id=blog_id)[0]
    context['blog'].author = User.objects.filter(
        user_id=context['blog'].author_id)[0]
    return render(request, "blog/detail.html", context)
