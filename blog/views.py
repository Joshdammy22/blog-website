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
from .util import *
import logging
from .util import create_follow_notification, delete_follow_notification
from django.contrib.auth import get_user_model

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)

@login_required
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

@login_required
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
@login_required
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
            
            # Create and save the comment
            comment = Comment.objects.create(
                blog=blog,
                author=request.user,
                content=comment_body,
            )
            print("DEBUG: Comment created successfully")

            # Get the author of the blog (recipient of the comment notification)
            recipient = blog.author  # Assuming the blog's author should receive the notification

            # Create a comment notification for the blog author
            create_comment_notification(sender=request.user, recipient=recipient, comment=comment)

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

from .util import create_reaction_notification

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

                # Create a notification for the blog's author (recipient)
                create_reaction_notification(sender=request.user, recipient=blog.author, blog=blog)
                print(f"DEBUG: Notification created for user {blog.author.username}")

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

@login_required
def mark_as_read(request, slug):
    if request.method == "POST":
        blog = get_object_or_404(Blog, slug=slug)
        blog.read_count += 1
        blog.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

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


@login_required
def toggle_follow(request, user_id):
    author = get_object_or_404(User, id=user_id)
    
    if request.user != author:  # Prevent users from following/unfollowing themselves
        follow, created = Follow.objects.get_or_create(follower=request.user, followee=author)
        if created:
            # If the follow was just created, send a notification to the followed user
            create_follow_notification(sender=request.user, recipient=author)
            print(f"DEBUG: Follow notification created for user {author.username}")
        else:
            # If the follow already exists, delete it (unfollow)
            follow.delete()
            print(f"DEBUG: User {request.user.username} unfollowed {author.username}")
            delete_follow_notification(sender=request.user, recipient=author)  # Notify about unfollow
    
    return redirect('profile', username=author.username)

from django.shortcuts import render
from django.db.models import Q
from .models import Blog
from users.models import CustomUser

@login_required
def search(request):
    query = request.GET.get('q', '')
    blogs = Blog.objects.none()
    authors = CustomUser.objects.none()

    if query:
        blogs = Blog.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        authors = CustomUser.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(profile__first_name__icontains=query) | 
            Q(profile__last_name__icontains=query)
        )

    context = {
        'query': query,
        'blogs': blogs,
        'authors': authors,
    }
    return render(request, 'blog/search_results.html', context)
