from django.shortcuts import render, redirect
from users.models import SubscriptionList
from users.forms import SubscriptionListForm
from users.models import *
from blog.models import Blog
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import uuid
from django.core.mail import send_mail
def home(request):
    print("Accessing home view...")  

    # Check if the user is authenticated
    if request.user.is_authenticated:
        print(f"User: '{request.user.username}' is authenticated, redirecting to the Home page.")  

        # Get the featured posts (limiting to 6 featured posts for example)
        featured_posts = Blog.objects.filter(featured=True)[:6]

        # Get the top 2 authors (you can adjust the logic here based on your actual use case)
        top_authors = Profile.objects.all()[:2]

        # Fetch the latest 6 posts ordered by 'created_at' (assuming 'created_at' is the field to order by)
        posts = Blog.objects.all().order_by('-created_at')[:6]  # Change from 'date_posted' to 'created_at'

        # Fetch a random or relevant list of recommended posts, filtering by categories, and excluding post with id=1 for demonstration
        recommended_posts = Blog.objects.filter(categories__name__in=['Tech', 'Business']).exclude(id=1)[:5]  # Correct filter on 'categories'

        # Check if the user is already subscribed
        subscription_exists = SubscriptionList.objects.filter(user=request.user).exists()
        
        # Handle the subscription form logic
        if request.method == 'POST':
            form = SubscriptionListForm(request.POST)
            if form.is_valid():
                user_email = form.cleaned_data['user_email']

                # If the user is already subscribed, show an info message
                if subscription_exists:
                    messages.info(request, "You are already subscribed.")
                    return redirect('home')
                else:
                    # Subscribe the user if the email matches the registered one
                    if user_email == request.user.email:
                        SubscriptionList.objects.create(user=request.user, user_email=user_email)
                        messages.success(request, "You have successfully subscribed!")
                        return redirect('home')
                    else:
                        # If emails don't match, redirect to email verification page
                        request.session['verification_email'] = user_email
                        return redirect('verify_email')
        else:
            # Pre-fill the form with the user's registered email if the method is GET
            print(f"Pre-filling subscription form with user's email: {request.user.email}")
            form = SubscriptionListForm(initial={'user_email': request.user.email})

        # Pass the form, subscription status, and post data to the template
        return render(request, 'home.html', {
            'user': request.user, 
            'form': form, 
            'subscription_exists': subscription_exists,
            'featured_posts': featured_posts,
            'top_authors': top_authors,
            'recent_posts': posts,
            'recommended_posts': recommended_posts,
        })
    else:
        # If no authenticated user, render the landing page
        print("User not authenticated, redirecting to the landing page.")
        return render(request, 'landing-page.html', {'user': request.user})





@login_required
def verify_email(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        email = request.session.get('verification_email')
        saved_token = request.session.get('verification_token')

        if token == saved_token:
            # Add the user to the subscription list
            SubscriptionList.objects.create(user=request.user, user_email=email)
            messages.success(request, "Email verified and subscription successful!")
            del request.session['verification_email']
            del request.session['verification_token']
            return redirect('home')
        else:
            messages.error(request, "Invalid verification token. Please try again.")

    return render(request, 'verify_email.html')