from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')
        cls.another_user = User.objects.create(username='another_test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user,
            group=cls.group
        )
        cls.user_post_url = (f'/{cls.user.username}/'
                             f'{cls.user.posts.all()[0].pk}/')
        cls.user_post_edit_url = (f'/{cls.user.username}/'
                                  f'{cls.user.posts.all()[0].pk}/edit/')
        cls.pages = [
            '/', '/group/test_slug/', '/new/', '/test_user/',
            cls.user_post_url, cls.user_post_edit_url
        ]
        cls.pages_for_guest_client = [
            '/', '/group/test_slug/', '/test_user/', cls.user_post_url
        ]
        cls.redirected_pages_for_guest_client = {
            '/new/':
                '/auth/login/?next=/new/',
            cls.user_post_edit_url:
                f'/auth/login/?next={cls.user_post_edit_url}',
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(PostsURLTests.another_user)

    def test_for_404_response(self):
        url = '/page_not_exist/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_for_guest_client(self):
        pages = PostsURLTests.pages_for_guest_client
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_guest_client_with_redirect(self):
        redirected_pages = PostsURLTests.redirected_pages_for_guest_client
        for url, redirect_url in redirected_pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_post_edit_for_not_author_and_guest_client(self):
        user_post_url = PostsURLTests.user_post_url
        user_post_edit_url = PostsURLTests.user_post_edit_url

        data = {
            self.guest_client: f'/auth/login/?next={user_post_edit_url}',
            self.another_authorized_client: user_post_url,
        }

        for user, url in data.items():
            with self.subTest(user=user):
                response = user.get(user_post_edit_url, follow=True)
                self.assertRedirects(response, url)

    def test_pages_for_authorized_client(self):
        for page in PostsURLTests.pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_uses_correct_template(self):
        user_post_edit = PostsURLTests.user_post_edit_url

        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group.html',
            '/new/': 'posts/new_post.html',
            user_post_edit: 'posts/new_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
