from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Follow

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')
        cls.another_user = User.objects.create(username='another_test_user')
        cls.the_third_user = User.objects.create(username='the_third_user')
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user
        )
        cls.post_another_user = Post.objects.create(
            text='test_text',
            author=cls.another_user
        )

    def setUp(self):
        cache.clear()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.__class__.user)

        self.another_authorized_user = Client()
        self.another_authorized_user.force_login(self.__class__.another_user)

        self.the_third_authorized_user = Client()
        self.the_third_authorized_user.force_login(
            self.__class__.the_third_user
        )

    def test_follow(self):
        """Проверяем, что авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок.
        """
        user = self.__class__.user
        another_user = self.__class__.another_user
        profile_follow_url = reverse(
            'profile_follow',
            kwargs={'username': another_user.username}
        )
        profile_unfollow_url = reverse(
            'profile_unfollow',
            kwargs={'username': another_user.username}
        )
        another_user_profile_url = reverse(
            'profile',
            kwargs={'username': another_user.username}
        )
        response = self.authorized_user.get(profile_follow_url)
        self.assertRedirects(response, another_user_profile_url)
        self.assertTrue(
            Follow.objects.filter(
                user=user,
                author=another_user
            ).exists()
        )
        response = self.authorized_user.get(profile_unfollow_url)
        self.assertRedirects(response, another_user_profile_url)
        self.assertFalse(
            Follow.objects.filter(
                user=user,
                author=another_user
            ).exists()
        )

    def test_post_on_wall_subscriber_non_subscriber(self):
        """Проверяем, что новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него.
        """
        another_user = self.__class__.another_user
        post = self.__class__.post_another_user

        follow_index_url = reverse('follow_index')

        profile_follow_url = reverse(
            'profile_follow',
            kwargs={'username': another_user.username}
        )
        self.authorized_user.get(profile_follow_url)
        response = self.authorized_user.get(follow_index_url)
        self.assertIn(post, response.context.get('page').object_list)
        response = self.the_third_authorized_user.get(follow_index_url)
        self.assertNotIn(post, response.context.get('page').object_list)
