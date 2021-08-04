from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import (require_http_methods, require_GET,
                                          require_POST)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.cache import cache

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def is_subscribed(user, follower):
    return Follow.objects.filter(user=user, author=follower).exists()


@require_GET
def index(request):
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = '1'

    page = cache.get(page_number)
    if page is None:
        posts = Post.objects.all()
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page_number)
        cache.set(page_number, page, timeout=20)

    return render(request, 'posts/index.html', {'page': page})


@require_GET
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html',
                  {'group': group, 'page': page})


@require_GET
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = is_subscribed(request.user, author)
    return render(request, 'posts/profile.html',
                  {'author': author, 'page': page, 'following': following})


@require_GET
def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    return render(request, 'posts/new_post.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username, post_id)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    return render(request, 'posts/new_post.html', {'form': form, 'post': post})


@login_required
@require_GET
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username, post_id)

    post.delete()
    return redirect('profile', username=username)


@login_required
@require_POST
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
        return redirect('post', username=username, post_id=post_id)

    return redirect('post', username=username, post_id=post_id)


@login_required
@require_GET
def follow_index(request):
    authors_id = []
    user = request.user
    followers = user.follower.all()
    for follower in followers:
        authors_id.append(follower.author.id)

    posts = Post.objects.filter(author__in=authors_id)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
@require_GET
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user

    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author,
        )

    return redirect('profile', username=username)


@login_required
@require_GET
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=user, author=author).delete()
    return redirect('profile', username=username)
