from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Blog, Notification, Comment

#Test Blog Creation
class BlogCreationTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_blog(self):
        # Log in the test user
        self.client.login(username='testuser', password='password')

        # Prepare blog data
        data = {
            'title': 'Test Blog Title',
            'content': 'Test content for the blog.',
            'slug': 'test-blog-title',
        }

        # Send POST request to create blog
        response = self.client.post(reverse('create_blog'), data)

        # Check if the blog is created and redirected
        self.assertEqual(response.status_code, 302)  # Redirect to the blog detail page
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Blog.objects.first().title, 'Test Blog Title')
        self.assertEqual(Blog.objects.first().author, self.user)

#Test Blog Publishing and Draft
class BlogPublishTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_blog_status_publish(self):
        self.client.login(username='testuser', password='password')

        # Prepare blog data with status 'Published'
        data = {
            'title': 'Test Blog Title',
            'content': 'Test content for the blog.',
            'slug': 'test-blog-title',
        }
        response = self.client.post(reverse('create_blog'), data)

        # Check if the blog is published
        blog = Blog.objects.first()
        self.assertEqual(blog.status, 1)  # Status should be Published
        self.assertRedirects(response, blog.get_absolute_url())

    def test_blog_status_draft(self):
        self.client.login(username='testuser', password='password')

        # Prepare blog data with status 'Draft'
        data = {
            'title': 'Test Blog Title',
            'content': 'Test content for the blog.',
            'slug': 'test-blog-title-draft',
        }
        response = self.client.post(reverse('create_blog'), data)

        # Check if the blog is saved as draft
        blog = Blog.objects.first()
        self.assertEqual(blog.status, 0)  # Status should be Draft


#Test Like a Blog
class BlogLikeTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_author = User.objects.create_user(username='author', password='password')
        self.blog = Blog.objects.create(
            title='Test Blog Title',
            content='Test content for the blog.',
            slug='test-blog-title',
            author=self.blog_author
        )

    def test_like_blog(self):
        self.client.login(username='testuser', password='password')

        # Like the blog
        response = self.client.get(reverse('like_blog', kwargs={'slug': self.blog.slug}))

        # Check if the like is added
        self.assertEqual(self.blog.total_likes(), 1)
        self.assertTrue(self.blog.likes.filter(id=self.user.id).exists())

    def test_unlike_blog(self):
        self.client.login(username='testuser', password='password')

        # Like the blog first
        self.blog.likes.add(self.user)

        # Unlike the blog
        response = self.client.get(reverse('like_blog', kwargs={'slug': self.blog.slug}))

        # Check if the like is removed
        self.assertEqual(self.blog.total_likes(), 0)
        self.assertFalse(self.blog.likes.filter(id=self.user.id).exists())

#Test Add Comment to Blog
class BlogCommentTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_author = User.objects.create_user(username='author', password='password')
        self.blog = Blog.objects.create(
            title='Test Blog Title',
            content='Test content for the blog.',
            slug='test-blog-title',
            author=self.blog_author
        )

    def test_add_comment(self):
        self.client.login(username='testuser', password='password')

        # Prepare comment data
        data = {'content': 'Test comment content.'}

        # Post comment to the blog
        response = self.client.post(reverse('add_comment', kwargs={'slug': self.blog.slug}), data)

        # Check if the comment is added
        self.assertEqual(self.blog.comments.count(), 1)
        self.assertEqual(self.blog.comments.first().content, 'Test comment content.')
        self.assertEqual(self.blog.comments.first().author, self.user)
        self.assertRedirects(response, self.blog.get_absolute_url())


#Test Follow User
class UserFollowTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.followee = User.objects.create_user(username='followee', password='password')

    def test_follow_user(self):
        self.client.login(username='testuser', password='password')

        # Follow the user
        response = self.client.get(reverse('follow_user', kwargs={'user_id': self.followee.id}))

        # Check if the follow relationship exists
        self.assertTrue(Follow.objects.filter(follower=self.user, followee=self.followee).exists())
        self.assertRedirects(response, reverse('profile', kwargs={'user_id': self.followee.id}))

    def test_unfollow_user(self):
        # First, follow the user
        Follow.objects.create(follower=self.user, followee=self.followee)

        self.client.login(username='testuser', password='password')

        # Unfollow the user
        response = self.client.get(reverse('follow_user', kwargs={'user_id': self.followee.id}))

        # Check if the follow relationship is deleted
        self.assertFalse(Follow.objects.filter(follower=self.user, followee=self.followee).exists())
        self.assertRedirects(response, reverse('profile', kwargs={'user_id': self.followee.id}))


#Test Notifications on Like
class NotificationTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_author = User.objects.create_user(username='author', password='password')
        self.blog = Blog.objects.create(
            title='Test Blog Title',
            content='Test content for the blog.',
            slug='test-blog-title',
            author=self.blog_author
        )

    def test_notification_on_like(self):
        self.client.login(username='testuser', password='password')

        # Like the blog
        self.client.get(reverse('like_blog', kwargs={'slug': self.blog.slug}))

        # Check if a notification was created
        notification = Notification.objects.filter(
            recipient=self.blog_author,
            sender=self.user,
            notification_type='like'
        ).first()

        self.assertIsNotNone(notification)
        self.assertEqual(notification.blog, self.blog)


#Test Notifications on Comment
class NotificationCommentTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.blog_author = get_user_model().objects.create_user(username='author', password='password')
        self.blog = Blog.objects.create(
            title='Test Blog Title',
            content='Test content for the blog.',
            slug='test-blog-title',
            author=self.blog_author
        )

    @patch('blog.signals.Notification.objects.create')  # Mock the signal's notification creation
    def test_notification_on_comment(self, mock_notification_create):
        self.client.login(username='testuser', password='password')

        # Add a comment
        self.client.post(reverse('add_comment', kwargs={'slug': self.blog.slug}), {'content': 'Test comment content.'})

        # Ensure that Notification.objects.create() was called once
        mock_notification_create.assert_called_once()

        # Ensure that the notification has the expected arguments
        args, kwargs = mock_notification_create.call_args
        self.assertEqual(kwargs['recipient'], self.blog_author)
        self.assertEqual(kwargs['sender'], self.user)
        self.assertEqual(kwargs['notification_type'], 'comment')
        self.assertEqual(kwargs['blog'], self.blog)
        self.assertEqual(kwargs['comment'].content, 'Test comment content.')


#Test Mark Notification as Read
class NotificationReadTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_author = User.objects.create_user(username='author', password='password')
        self.blog = Blog.objects.create(
            title='Test Blog Title',
            content='Test content for the blog.',
            slug='test-blog-title',
            author=self.blog_author
        )

        # Create a notification
        self.notification = Notification.objects.create(
            recipient=self.user,
            sender=self.blog_author,
            notification_type='like',
            blog=self.blog
        )

    def test_mark_notification_as_read(self):
        self.client.login(username='testuser', password='password')

        # Mark the notification as read
        response = self.client.get(reverse('mark_as_read', kwargs={'notification_id': self.notification.id}))

        # Check if the notification is marked as read
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
