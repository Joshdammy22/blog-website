from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *


def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            # Check which button was clicked
            if 'post_button' in request.POST:
                blog.status = 1  # Published
            else:
                blog.status = 0  # Draft
            blog.save()
            return redirect('blog/blog_detail', slug=blog.slug)
    else:
        form = BlogForm()

    return render(request, 'blog/create_blog.html', {'form': form})

def blog_list(request):
    blogs = Blog.objects.filter(status=1)
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=1)
    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def like_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if blog.likes.filter(id=request.user.id).exists():
        blog.likes.remove(request.user)
    else:
        blog.likes.add(request.user)
        Notification.objects.create(
            recipient=blog.author,
            sender=request.user,
            notification_type='like',
            blog=blog
        )
    return redirect(blog.get_absolute_url())

@login_required
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=1)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.blog = blog
            comment.save()
            Notification.objects.create(
                recipient=blog.author,
                sender=request.user,
                notification_type='comment',
                blog=blog,
                comment=comment
            )
            return redirect(blog.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form, 'blog': blog})

@login_required
def follow_user(request, user_id):
    followee = get_object_or_404(User, id=user_id)
    if request.user != followee:
        existing_follow = Follow.objects.filter(follower=request.user, followee=followee)
        if existing_follow.exists():
            existing_follow.delete()
        else:
            Follow.objects.create(follower=request.user, followee=followee)
            Notification.objects.create(
                recipient=followee,
                sender=request.user,
                notification_type='follow'
            )
    return redirect('profile', user_id=user_id)

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'blog/notification_list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')
