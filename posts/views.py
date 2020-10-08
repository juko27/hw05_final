from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Post, Group
from .forms import PostForm


def index(request):
        post_list = Post.objects.all()
        paginator = Paginator(post_list, 10) 

        page_number = request.GET.get('page')  
        page = paginator.get_page(page_number)  
        return render(
            request,
            'index.html',
            {'page': page, 'paginator': paginator}
        ) 


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)
    
    return render(request, 
                  "group.html", 
                  {"group": group, 'page': page, 'paginator': paginator})


@login_required()
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
        profile = get_object_or_404(User, username=username)
        posts = profile.posts.all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        return render(request, 'profile.html', 
                    {
                        'profile' : profile, 
                        'posts': posts, 
                        'page': page, 
                        'paginator': paginator
                    })


def post_exist(fn):
    def post_check(request, username, post_id):
        try:
            return fn(request, username, post_id)
        except Post.DoesNotExist:
            return redirect('profile', username)
    return post_check


@post_exist
def post_view(request, username, post_id):
        profile = get_object_or_404(User, username=username)
        posts_len = profile.posts.all().count()
        post = Post.objects.get(id=post_id)
        if profile != post.author:
            return redirect('profile', profile.username)
        return render(request, 'post.html', {'post': post, 
                      'profile': profile, 'posts': posts_len})


@post_exist
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = Post.objects.get(id=post_id)
    if request.user != author:   
        return redirect('post', post.author, post_id)
    form = PostForm(request.POST, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {'post': post, 'form': form}) 
