from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def get_a_page(posts, request):
    page_number = request.GET.get('page')
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page = paginator.get_page(page_number)
    return page


def index(request):
    posts = Post.objects.all()
    page = get_a_page(posts, request)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = get_a_page(posts, request)
    return render(request, 'posts/group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        n_post = form.save(commit=False)
        n_post.author = request.user
        n_post.save()
        return redirect('index')
    context = {
        'form': form,
        'is_new': True,
    }
    return render(request, 'posts/post_new.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page = get_a_page(posts, request)
    context = {
        'author': author,
        'page': page,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    context = {
        'author': post.author,
        'post': post,
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    context = {
        'form': form,
        'is_new': False,
    }
    return render(request, 'posts/post_new.html', context)
