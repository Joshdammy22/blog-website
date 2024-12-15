from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import JsonResponse
from django.core.paginator import Paginator


# View to create a blog post
def create_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        slug = request.POST.get('slug')
        
        blog = Blog.objects.create(
            title=title,
            content=content,
            slug=slug,  # Ensure slug is passed correctly
            status=0,  # Draft or Published status
            author=request.user
        )
        
        # Redirect to the blog detail page using the slug
        return redirect('blog_detail', slug=blog.slug)

from django.urls import reverse

def get_absolute_url(self):
    return reverse("blog_detail", kwargs={"slug": self.slug})


# View to list all published blog posts
def blog_list(request):
    blogs = Blog.objects.filter(status=1)  # Only show published blogs
    paginator = Paginator(blogs, 5)  # Show 5 blogs per page

    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    return render(request, 'blog/blogs.html', {'page_obj': page_obj})

# View to see the details of a specific blog post by its slug
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog/blog_detail.html', {'blog': blog})

# View to like a blog post
@login_required
def like_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if blog.likes.filter(id=request.user.id).exists():
        blog.likes.remove(request.user)
    else:
        blog.likes.add(request.user)
        # Create a notification when a user likes a post
        Notification.objects.create(
            recipient=blog.author,
            sender=request.user,
            notification_type='like',
            blog=blog
        )
    return redirect(blog.get_absolute_url())  # Redirect back to the blog's detail page

# View to add a comment to a blog post
@login_required
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=1)  # Only allow comments on published blogs
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.blog = blog
            comment.save()
            return redirect(blog.get_absolute_url())  # Redirect to the blog detail page
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form, 'blog': blog})


# View to follow a user
@login_required
def follow_user(request, user_id):
    followee = get_object_or_404(User, id=user_id)
    if request.user != followee:
        existing_follow = Follow.objects.filter(follower=request.user, followee=followee)
        if existing_follow.exists():
            existing_follow.delete()  # Unfollow the user
        else:
            Follow.objects.create(follower=request.user, followee=followee)  # Follow the user
            # Create a notification when the user follows another user
            Notification.objects.create(
                recipient=followee,
                sender=request.user,
                notification_type='follow'
            )
    return redirect('profile', user_id=user_id)  # Redirect to the followed user's profile


# View to list all notifications for the current user
@login_required
def notification_list(request):
    notifications = request.user.notifications.all()  # Get all notifications for the logged-in user
    return render(request, 'blog/notification_list.html', {'notifications': notifications})


# View to mark a notification as read
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()  # Mark the notification as read
    return redirect('notification_list')  # Redirect back to the notification list page


# View to mark all notifications as read
@login_required
def mark_all_as_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)  # Mark all as read
        return JsonResponse({'success': True, 'message': 'All notifications marked as read.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)  # Handle invalid request method
