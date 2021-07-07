from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'group': group, })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    user_posts = author.posts.all()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    user_post_count = user_posts.count()
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists())
    context = {
        'author': author,
        'page': page,
        'count': user_post_count,
        'following': following
    }
    return render(
        request,
        'profile.html',
        context,
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author'),
                             id=post_id, author__username=username)
    form = CommentForm(instance=None)
    comments = post.post_comments.all()
    context = {
        'post': post,
        'author': post.author,
        'count': post.author.posts.count,
        'comments': comments,
        'form': form,
    }
    return render(
        request,
        'post.html',
        context,
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html',
                      {'form': form, 'switch': 'new'})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    post_item = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post_item.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post_item)
    if not form.is_valid():
        return render(request, 'new_post.html',
                      {'form': form, 'switch': 'edit'})
    form.save()
    return redirect('post', username=username, post_id=post_id)


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
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.post_comments.all()
    form = CommentForm(
        request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', post_id=post_id,
                        username=username)
    return render(request, 'includes/comments.html',
                  {'form': form, 'comments': comments, 'post': post})


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
        return redirect('index')
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.filter(author=author, user=request.user).delete()
        return redirect('profile', username=username)
    redirect('profile', username=username)
