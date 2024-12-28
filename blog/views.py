from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

import logging


# Set up logging
logger = logging.getLogger(__name__)


def create_blog(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        print("Raw POST data:", request.POST)
        print("Raw FILES data:", request.FILES)

        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid. Data:", form.cleaned_data)

            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()

            # Save categories and tags
            blog.categories.set(form.cleaned_data['categories'])
            blog.tags.set(form.cleaned_data['tags'])

            messages.success(request, "Your blog has been created successfully!")
            return redirect('blog_detail', slug=blog.slug)
        else:
            print("Form is invalid. Errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = BlogForm()
        print("GET request received. Initialized form.")

    return render(request, 'blog/create_blog.html', {
        'form': form,
        'categories': categories,
        'tags': json.dumps(list(tags.values('id', 'name')), cls=DjangoJSONEncoder),
    })


def update_blog(request, slug):
    # Fetch the blog instance by slug
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == 'POST':
        # Use BlogUpdateForm for updating the blog instance
        form = BlogUpdateForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'The blog has been updated successfully.') 
            # Redirect to the blog detail page using the slug
            return redirect('blog_detail', slug=blog.slug)
        
    else:
        form = BlogUpdateForm(instance=blog)
        # Get pre-selected categories and tags
        selected_categories = blog.categories.values_list('id', flat=True)
        selected_tags = blog.tags.values_list('id', flat=True)

    return render(request, 'blog/update_blog.html', {
        'form': form,
        'selected_categories': selected_categories,
        'selected_tags': selected_tags,
    })


@login_required
def delete_blog(request, slug):
    """
    Handles the deletion of a blog by the logged-in user.
    """
    blog = get_object_or_404(Blog, slug=slug, author=request.user)

    if request.method == "POST":
        blog.delete()
        messages.success(request, 'The blog has been deleted successfully.') 
        return HttpResponseRedirect(reverse('my_blogs'))

    context = {'blog': blog}
    return render(request, 'users/confirm_delete.html', context)

# View to list all published blog posts
def blog_list(request):
    blogs = Blog.objects.filter(status=1)  # Only show published blogs
    paginator = Paginator(blogs, 5)  # Show 5 blogs per page

    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    return render(request, 'blog/blogs.html', {'page_obj': page_obj, 'blogs':blogs})


@login_required
def blog_detail(request, slug):
    print(f"DEBUG: Entering blog_detail view with slug: {slug}")

    # Retrieve the blog by slug
    blog = get_object_or_404(Blog, slug=slug)
    print(f"DEBUG: Retrieved blog '{blog.title}' (ID: {blog.id}) by {blog.author}")

    # Track views
    if not request.session.get(f"viewed_{slug}", False) and request.user != blog.author:
        blog.read_count += 1
        blog.save()
        request.session[f"viewed_{slug}"] = True
        print(f"DEBUG: Incremented read count for blog '{blog.title}'. New count: {blog.read_count}")

    # Handle comment submission
    if request.method == 'POST':
        print("DEBUG: Received POST request for comment submission")
        comment_body = request.POST.get('comment_body')
        if comment_body:
            print(f"DEBUG: Creating comment for blog '{blog.title}' by user '{request.user.username}'")
            Comment.objects.create(
                blog=blog,
                author=request.user,
                content=comment_body,
            )
            print("DEBUG: Comment created successfully")
            return HttpResponseRedirect(request.path_info)  # Redirect to the same page

    # Get reaction summary counts for each reaction type
    reactions_summary = {reaction_type: blog.get_reaction_count(reaction_type) for reaction_type in REACTION_CHOICES}
    print(f"DEBUG: Reactions summary: {reactions_summary}")

    # Get the user's current reaction
    current_reaction = None
    if request.user.is_authenticated:
        user_reaction = blog.reactions.filter(user=request.user).first()
        current_reaction = user_reaction.reaction_type if user_reaction else None
        print(f"DEBUG: Current reaction by user '{request.user.username}': {current_reaction}")

    # Render the template
    print(f"DEBUG: Rendering blog_detail template for blog '{blog.title}'")
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'reactions_summary': reactions_summary,
        'current_reaction': current_reaction,
        'slug': slug,
    })

REACTION_CHOICES = ['like', 'love', 'haha', 'wow', 'applaud']

@login_required
def save_reaction(request, slug):
    # Debugging output
    print(f"DEBUG: Entering save_reaction view with slug: {slug}")
    
    if request.method == 'POST':
        try:
            # Get the blog by slug
            blog = get_object_or_404(Blog, slug=slug)
            print(f"DEBUG: Retrieved blog '{blog.title}' (ID: {blog.id}) for reaction update")
            
            # Parse the request body
            data = json.loads(request.body)
            reaction_type = data.get('reaction')
            print(f"DEBUG: Received POST data: {data}")

            # Check if the reaction is valid
            if reaction_type not in REACTION_CHOICES:
                print(f"DEBUG: Invalid reaction type: {reaction_type}")
                return JsonResponse({'success': False, 'message': 'Invalid reaction type'})

            # Check if the user has already reacted to the blog
            existing_reaction = blog.reactions.filter(user=request.user).first()
        
            if existing_reaction:
                # If the user has reacted with a different reaction type, update their reaction
                if existing_reaction.reaction_type != reaction_type:
                    existing_reaction.reaction_type = reaction_type
                    existing_reaction.save()
                    print(f"DEBUG: Updated existing reaction to '{reaction_type}'")
                # If the user has already reacted with the same reaction type, do nothing
                else:
                    print(f"DEBUG: User already reacted with '{reaction_type}', no update needed")
            else:
                # If the user hasn't reacted yet, create a new reaction
                blog.reactions.create(user=request.user, reaction_type=reaction_type)
                print(f"DEBUG: Created new reaction '{reaction_type}' for user {request.user.username}")

            # Get updated reaction counts
            reactions_summary = {reaction: blog.reactions.filter(reaction_type=reaction).count() for reaction in REACTION_CHOICES}
            print(f"DEBUG: Updated reaction summary: {reactions_summary}")

            # Get current reaction for the user
            current_reaction = blog.reactions.filter(user=request.user).first().reaction_type if existing_reaction else reaction_type

            # Return the updated data
            return JsonResponse({
                'success': True,
                'reaction_summary': reactions_summary,
                'current_reaction': current_reaction
            })

        except Exception as e:
            print(f"DEBUG: Error occurred: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def mark_as_read(request, slug):
    if request.method == "POST":
        blog = get_object_or_404(Blog, slug=slug)
        blog.read_count += 1
        blog.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


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


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Follow

@login_required
def toggle_follow(request, user_id):
    author = get_object_or_404(User, id=user_id)
    
    if request.user != author:  # Prevent users from following themselves
        follow, created = Follow.objects.get_or_create(follower=request.user, followee=author)
        if not created:
            # If the follow already exists, it means the user wants to unfollow
            follow.delete()
    
    return redirect('profile', user_id=user_id)
