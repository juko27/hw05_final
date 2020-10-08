from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Group


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
        
    def post_view(self, url, post = None):
        if post is None: post = self.post
        self.response = self.client.get(url)
        if self.response.context.get("paginator"):
            res = self.response.context["paginator"].object_list[0]
        else:
            res = self.response.context["post"]
        return self.assertEqual(res, post)
        
    def test_new_post_in_pages(self):
        self.post_view("/")
        self.post_view(f"/{self.user.username}/")
        self.post_view(f"/{self.user.username}/{self.post.id}/")
        self.post_view(f"/group/{self.group.slug}/")
        
    def test_post_edit(self):
        response = self.client.post(f"/{self.user.username}/{self.post.id}/edit/", 
            {'text': 'New text', 'group': self.group})
        post = Post.objects.get(id = self.post.id )

        self.post_view("/", post)
        self.post_view(f"/{self.user.username}/", post)
        self.post_view(f"/{self.user.username}/{self.post.id}/", post)
