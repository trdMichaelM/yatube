from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from ..models import Post

User = get_user_model()


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.__class__.user)

    def test_comment(self):
        """Проверяем, что только авторизированный пользователь
        может комментировать посты.
        """
        user = self.__class__.user
        post = self.__class__.post
        add_comment_url = reverse(
            'add_comment',
            kwargs={'username': user.username, 'post_id': post.id}
        )
        post_url = reverse(
            'post',
            kwargs={'username': user.username, 'post_id': post.id}
        )
        redirect_url = f'/auth/login/?next={add_comment_url}'
        form_data = {
            'text': 'test comment'
        }
        response = self.guest_client.post(
            add_comment_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, redirect_url)
        response = self.authorized_user.post(
            add_comment_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, post_url)
