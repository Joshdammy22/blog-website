from django.shortcuts import render, get_object_or_404
from .models import User
from blog.models import Follow

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    blogs = user.blog_set.filter(status=1)  # Published blogs
    followers = user.followers.count()
    following = user.following.count()
    is_following = Follow.objects.filter(follower=request.user, followee=user).exists() if request.user.is_authenticated else False
    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'blogs': blogs,
        'followers': followers,
        'following': following,
        'is_following': is_following,
    })
