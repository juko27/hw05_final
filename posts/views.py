from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm


@cache_page(20, key_prefix='index_page')
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
    form = PostForm(request.POST or None, files=request.FILES or None) 
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
        followers = Follow.objects.filter(author=profile).count()
        follows = Follow.objects.filter(user=profile).count()
        following = True
        if request.user.id != None:
            try:
                Follow.objects.get(user=request.user, author=profile)
                
            except Follow.DoesNotExist:
                following = False
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page') 
        page = paginator.get_page(page_number) 
        return render(request, 'profile.html',  
                    { 
                        'profile' : profile,  
                        'posts': posts, 
                        'following': following, 
                        'follows': follows,
                        'followers': followers,
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
        comments = post.comments.all()
        form = CommentForm()
        if profile != post.author: 
            return redirect('profile', profile.username) 
        return render(request, 'post.html', {
                            'post': post,  
                            'profile': profile, 
                            'posts': posts_len, 
                            'comments': comments, 
                            'form': form
                        }) 
 
 
@post_exist 
def post_edit(request, username, post_id): 
    post = Post.objects.get(id=post_id, author__username=username) 
    if request.user.username != username:    
        return redirect('post', post.author, post_id) 
    form = PostForm(request.POST or None, 
                    files=request.FILES or None, 
                    instance=post)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id) 
    return render(request, 'new_post.html', {'post': post, 'form': form})  


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username) 
    post = get_object_or_404(Post, pk=post_id, author=author) 
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False) 
            comment.author = request.user 
            comment.post = post
            comment.save() 
    return redirect("post", username=username, 
                            post_id=post_id) 
        
    
def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500) 


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user).order_by("-pub_date")
      
    paginator = Paginator(post_list, 10)  
    page_number = request.GET.get('page')   
    page = paginator.get_page(page_number)  
    return render(request, 'follow.html', {
                        'page': page,  
                        'paginator': paginator
                        }) 


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username) 
    if author!=request.user:
        Follow.objects.get_or_create(user = request.user, author = author)
   
    return redirect('profile', username) 


@login_required
def profile_unfollow(request, username):
    unfollow = Follow.objects.get(user = request.user, author__username=username)
    unfollow.delete()
    return redirect('profile', username)
