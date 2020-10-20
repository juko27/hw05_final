import time

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.cache import cache 
from django.urls import reverse
from django.test import override_settings
from tempfile import NamedTemporaryFile, gettempdir

from .models import Post, Group, Follow


URLS = {
        'profile': ['user_name'], 
        'index': [],
        'post': ['user_name', '1'], 
        'group': ['group']
        }


class TestRegMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username='user_name', 
                password='pass_word'
        )
        self.client.force_login(self.user)
        self.logout_user = Client()
       
    def test_profile(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['profile'], User)
        self.assertEqual(response.context['profile'].username, self.user.username) 
        self.assertTemplateUsed(template_name='profile')

    def test_auth_new_post(self):
        response = self.client.post(reverse('new'), {'text': 'sometext'})
        post = Post.objects.last()
        self.assertEqual(post.text, 'sometext')
        self.assertRedirects(response, reverse('index'))
        
    def test_not_auth_new_post(self):
        response = self.logout_user.post(reverse('new'), {'text': 'logout_test'})
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("new")}')


class TestPostMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username='user_name', password='pass_word'
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title='Group',
            description='description',
            slug = 'group'
        )
        self.post = Post.objects.create(
            text='Text', 
            author=self.user, 
            group=self.group
        )
        
    def post_view(self, post = None):
        cache.clear()
        for path in URLS:
            if post is None: post = self.post
            self.response = self.client.get(reverse(path, args=URLS[path]))
            if self.response.context.get('paginator'):
                res = self.response.context['paginator'].object_list[0]
            else:
                res = self.response.context['post']
            return self.assertEqual(res, post)
        
    def test_new_post_in_pages(self):
        self.post_view()
        
    def test_post_edit(self): 
        self.client.post(reverse('post_edit', args = [self.user.username, self.post.id]), 
            {'text': 'New text', 'group': self.group}) 
        post = Post.objects.get(id = self.post.id) 
 
        self.post_view(post) 


class TestImageAndCacheMethods(TestCase):

    @override_settings(MEDIA_ROOT=gettempdir())
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username='user_name', password='pass_word'
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title='Group', 
            description='description', 
            slug = 'group'
        )
        img = NamedTemporaryFile(suffix='.jpg').name
        self.post = Post.objects.create(
            text='Text', 
            author=self.user, 
            group=self.group,
            image=img
        )
    
    def test_img_in_pages(self):
        for key, value in URLS.items():
            response = self.client.get(reverse(key, args=value))
            self.assertContains(response, '<img')

    def test_load_not_img_format(self):
        with NamedTemporaryFile(mode='w+b') as not_img:
            not_img.write('abcdefg'.encode())
            not_img.seek(0)
            post = self.client.post(reverse('post_edit', 
                        args = [self.user.username, self.post.id]), 
                        {'image': not_img}) 
        self.assertFormError(post, 'form', 'image', 
            f'Загрузите правильное изображение.'
            f' Файл, который вы загрузили, поврежден или не является изображением.')

    def test_cache(self):
        start = time.time()
        self.client.get(reverse('index'))
        res1 = time.time() - start

        start_cache = time.time()
        self.client.get(reverse('index'))
        res2 = time.time() - start_cache
        self.assertTrue(res2 < res1)


class TestFollowMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
                username='user_name', password='pass_word'
        )
        self.not_interesting_author = User.objects.create_user(
                username='qwerty', password='qwerty'
        )
        self.follower = User.objects.create_user(
                username='follower', password='follower'
        )
        
        self.client.force_login(self.follower)
        self.logout_user = Client()
        for i in range(4):
            self.post = Post.objects.create(
                text=i, 
                author=self.author
            )
            if i%2==0:
                self.post = Post.objects.create(
                text=i, 
                author=self.not_interesting_author
            )

    def test_folllow_unfollow(self):
        self.client.post(reverse('profile_follow', args=[self.author.username]))
        follow = Follow.objects.get(user=self.follower)
        self.assertIsNotNone(follow)

        self.client.post(reverse('profile_unfollow', args=[self.author.username]))
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(user=self.follower)

    def test_folllow_index(self):
        self.client.post(reverse('profile_follow', args=[self.author.username]))
        response = self.client.get(reverse('follow_index'))
        author_posts = self.author.posts.all()
        follow_posts = response.context['paginator'].object_list
        self.assertEqual((len(follow_posts)), len(author_posts))
        for post in follow_posts:
            self.assertEqual(post.author.username, self.author.username)

    def test_comment(self):
        response = self.logout_user.post(reverse('add_comment', 
                   args=[self.author.username, self.author.posts.first().id]), 
                   {'text': 'comment'})
        self.assertRedirects(response, f'{reverse("login")}'
        f'?next={reverse("add_comment", args=[self.author.username, self.author.posts.first().id])}')
