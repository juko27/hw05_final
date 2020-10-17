from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.cache import cache 
from django.urls import reverse
from django.test import override_settings
from tempfile import NamedTemporaryFile, gettempdir
import time
from .models import Post, Group


URLS = {'profile': ['user_name'], 
                'index': [],
                'post': ['user_name', '1'], 
                'group': ['group']}


class TestRegMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username="user_name", 
                password="pass_word"
        )
        self.client.force_login(self.user)
        self.logout_user = Client()
       
    def test_profile(self):
        response = self.client.get("/user_name/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["profile"], User)
        self.assertEqual(response.context["profile"].username, self.user.username) 
        self.assertTemplateUsed(template_name='profile')

    def test_auth_new_post(self):
        response = self.client.post('/new/', {'text': 'sometext'})
        post = Post.objects.last()
        self.assertEqual(post.text, 'sometext')
        self.assertRedirects(response, '/')
        
    def test_not_auth_new_post(self):
        response = self.logout_user.post('/new/', {'text': 'logout_test'})
        self.assertRedirects(response,f"{reverse('login')}?next={reverse('new')}")


class TestPostMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username="user_name", password="pass_word"
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title="Group", 
            description="description", 
            slug = "group"
        )
        self.post = Post.objects.create(
            text="Text", 
            author=self.user, 
            group=self.group
        )
        
    def post_view(self, post = None):
        cache.clear()
        for path in URLS:
            if post is None: post = self.post
            self.response = self.client.get(reverse(path, args = URLS[path]))
            if self.response.context.get("paginator"):
                res = self.response.context["paginator"].object_list[0]
            else:
                res = self.response.context["post"]
            return self.assertEqual(res, post)
        
    def test_new_post_in_pages(self):
        self.post_view()
        
    def test_post_edit(self):
        self.client.post(reverse('post_edit', args = [self.user.username, self.post.id]),
            {'text': 'New text', 'group': self.group})
        post = Post.objects.get(id = self.post.id )

        self.post_view(post)


class TestImageAndCacheMethods(TestCase):

    @override_settings(MEDIA_ROOT=gettempdir())
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username="user_name", password="pass_word"
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title="Group", 
            description="description", 
            slug = "group"
        )
        img = NamedTemporaryFile(suffix=".jpg").name
        self.post = Post.objects.create(
            text="Text", 
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
