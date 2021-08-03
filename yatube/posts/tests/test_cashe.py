from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from ..models import Post

User = get_user_model()


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')

    def setUp(self):
        cache.clear()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.__class__.user)

    def test_cache(self):
        """Тест кэширования главной страницы."""
        user = self.__class__.user
        post = Post.objects.create(
            text='test_text',
            author=user
        )
        index_url = reverse('index')
        response = self.authorized_user.get(index_url)
        posts = response.context['page'].object_list
        posts_count = len(posts)
        self.assertIn(post, posts)
        post.delete()
        response = self.authorized_user.get(index_url)
        posts = response.context['page'].object_list
        self.assertEqual(len(posts), posts_count)
        cache.clear()
        response = self.authorized_user.get(index_url)
        posts = response.context['page'].object_list
        self.assertEqual(len(posts), posts_count - 1)
