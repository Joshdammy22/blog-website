from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.text import slugify

# Tag model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

# Category model
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# Blog model
STATUS = (
    (0, 'Draft'),
    (1, 'Published')
)

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateField(auto_now=True)
    modified_at = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=0)
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True)
    featured = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='blogs', blank=True)

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_reaction_summary(self):
        return self.reactions.values('reaction_type').annotate(count=models.Count('reaction_type'))
    
    def get_reaction_count(self, reaction_type):
        return self.reactions.filter(reaction_type=reaction_type).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog_detail", kwargs={"slug": self.slug})

# Reaction model
REACTION_CHOICES = (
    ('like', 'Like'),
    ('love', 'Love'),
    ('haha', 'Haha'),
    ('wow', 'Wow'),
    ('sad', 'Sad'),
    ('angry', 'Angry'),
    ('applaud', 'Applaud'),
)

class Reaction(models.Model):
    blog = models.ForeignKey(Blog, related_name='reactions', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('blog', 'user')  # Prevent a user from reacting multiple times to the same blog
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} to {self.blog.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.blog.author != self.user:
            Notification.objects.create(
                recipient=self.blog.author,
                sender=self.user,
                notification_type='reaction',
                blog=self.blog
            )

# Comment model
class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"

# Follow model
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('follower', 'followee')
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}"

# Notification model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('reaction', 'Reaction'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type.capitalize()} by {self.sender.username} to {self.recipient.username}"
