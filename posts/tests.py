from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post


class TestRegMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username="user_name", password="pass_word"
        )
        self.client.login(username='user_name', password='pass_word')
       
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
        self.client.logout()
        response = self.client.post('/new/', {'text': 'logout_test'})
        self.assertRedirects(response,f"{reverse('login')}?next={reverse('new')}")

class TestPostMethods(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                username="user_name", password="pass_word"
        )
        self.client.login(username='user_name', password='pass_word')
        self.post = Post.objects.create(text="Text", author=self.user)
        self.response_index = self.client.get("/")
        self.response_profile = self.client.get(f"/{self.user.username}/")
        self.response_post = self.client.get\
            (f"/{self.user.username}/{self.post.id}/")
       
    def test_new_post_in_pages(self):
        
        self.assertEqual(self.response_index.context["paginator"].\
            object_list[0].id, self.post.id)
        self.assertEqual(self.response_profile.context["paginator"].\
            object_list[0].id, self.post.id)
        self.assertEqual(self.response_post.context["post"].id, self.post.id)
        
    def test_post_edit(self):
        response = self.client.post(f"/{self.user.username}/{self.post.id}/edit/", 
            {'text': 'New text'})
        post = Post.objects.get(id = self.post.id )
        self.assertEqual(post, self.post)
        self.assertEqual(self.response_index.context["paginator"].\
            object_list[0].text, post.text)
        self.assertEqual(self.response_index.context["paginator"].\
            object_list[0].text, post.text)

        r = self.client.get(f"/{self.user.username}/{self.post.id}/")

        self.assertEqual(r.context["post"].text, post.text)
