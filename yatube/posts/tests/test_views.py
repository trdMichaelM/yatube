import shutil

from http import HTTPStatus

from django.core.paginator import Page
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEST_DIR = 'test_data'


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class PostsViewsTests(TestCase):
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
            author=cls.user
        )
        cls.another_post = Post.objects.create(
            text='mazafaka',
            author=cls.user,
            group=cls.group,
        )
        cls.another_group = Group.objects.create(
            title='another_test_group',
            slug='another_test_group_slug',
            description='another_test_group_description'
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.post_with_image = Post.objects.create(
            text='post with image for test',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_DIR)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(PostsViewsTests.user)
        self.another_authorized_user = Client()
        self.another_authorized_user.force_login(PostsViewsTests.another_user)

    def test_pages_use_correct_template(self):
        """Тест шаблонов"""
        templates_page_names = {
            'posts/index.html': reverse('index'),
            'posts/group.html': reverse('group_posts',
                                        kwargs={'slug': 'test_slug'}),
            'posts/new_post.html': reverse('new_post'),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        главной страницы.
        """
        response = self.authorized_user.get(reverse('index'))
        self.assertIsInstance(response.context['page'], Page)

    def test_group_posts_correct_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        страницы группы.
        """
        response = self.authorized_user.get(
            reverse('group_posts', kwargs={'slug': 'test_slug'})
        )
        self.assertIsInstance(response.context['group'], Group)
        self.assertIsInstance(response.context['page'], Page)

    def test_new_post_correct_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        страницы создания поста.
        """
        response = self.authorized_user.get(reverse('new_post'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        страницы редактирования поста /<username>/<post_id>/edit/.
        """
        user = PostsViewsTests.user
        link = reverse(
            'post_edit',
            kwargs={'username': user.username, 'post_id': self.post.id}
        )
        response = self.authorized_user.get(link)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_profile_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        страницы профайла пользователя /<username>/.
        """
        user = PostsViewsTests.user
        link = reverse(
            'profile',
            kwargs={'username': user.username}
        )
        response = self.authorized_user.get(link)
        self.assertIsInstance(response.context['author'], User)
        self.assertIsInstance(response.context['page'], Page)

    def test_post_context(self):
        """Проверяем, соответствует ли ожиданиям словарь context
        страницы отдельного поста /<username>/<post_id>/.
        """
        user = PostsViewsTests.user
        link = reverse(
            'post',
            kwargs={'username': user.username, 'post_id': self.post.id}
        )
        response = self.authorized_user.get(link)
        self.assertIsInstance(response.context['author'], User)
        self.assertIsInstance(response.context['post'], Post)

    def test_contains_picture_in_context_with_paginator(self):
        """Проверяем, что при выводе поста с картинкой изображение передаётся
        в словаре context: на главную страницу, на страницу профайла,
        на страницу группы.
        """
        user = PostsViewsTests.user
        post_with_image = self.__class__.post_with_image

        index_url = reverse('index')
        profile_url = reverse(
            'profile',
            kwargs={'username': user.username}
        )
        group_url = reverse('group_posts', kwargs={'slug': 'test_slug'})
        urls = [index_url, profile_url, group_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                posts = response.context['page'].object_list
                index_of_post_with_image = posts.index(post_with_image)
                self.assertTrue(posts[index_of_post_with_image].image)

    def test_contains_picture_in_context_no_paginator(self):
        """Проверяем, что при выводе поста с картинкой изображение передаётся
        на отдельную страницу поста.
        """
        user = PostsViewsTests.user
        post_with_image = self.__class__.post_with_image
        post_url = reverse(
            'post',
            kwargs={'username': user.username,
                    'post_id': post_with_image.id}
        )
        response = self.authorized_user.get(post_url)
        post = response.context['post']
        self.assertTrue(post.image)

    def test_created_new_post_on_home_page(self):
        """Проверяем, что если при создании поста указать группу,
        то этот пост появляется на главной странице сайта.
        """
        post = PostsViewsTests.another_post

        response = self.authorized_user.get(reverse('index'))
        self.assertIn(post, response.context.get('page').object_list)

    def test_created_new_post_on_group_page(self):
        """Проверяем, что если при создании поста указать группу,
        то этот пост появляется на странице выбранной группы.
        """
        post = PostsViewsTests.another_post

        response = self.authorized_user.get(
            reverse('group_posts', kwargs={'slug': 'test_slug'})
        )
        self.assertIn(post, response.context.get('page').object_list)

    def test_created_new_post_not_on_another_group_page(self):
        """Проверяем, что если при создании поста указать группу,
        то этот пост не попал в группу, для которой не был предназначен.
        """
        post = PostsViewsTests.another_post

        response = self.authorized_user.get(
            reverse('group_posts', kwargs={'slug': 'another_test_group_slug'})
        )
        self.assertNotIn(
            post,
            response.context.get('page').object_list
        )

    def test_create_new_post_by_guest_client(self):
        """Проверяем, что не авторизованный пользователь редиректится
        со страницы создания нового поста.
        """
        url = reverse('new_post')
        redirect_url = '/auth/login/?next=/new/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, redirect_url)

    def test_create_new_post_by_authorized_user(self):
        """Проверяем, что авторизованному пользователю доступна
        страница создания поста.
        """
        url = reverse('new_post')
        response = self.authorized_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_post_right_author(self):
        """Проверяем, что пост создается с правильным автором."""
        user = PostsViewsTests.user
        url = reverse('new_post')
        text = 'some text here fot check author'
        form_data = {
            'text': text
        }
        self.authorized_user.post(
            url,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=text,
                author=user,
                group__isnull=True
            ).exists()
        )

    def test_post_edit_not_author(self):
        """Проверяем, что не автор не может редактировать пост."""
        post = PostsViewsTests.post
        another_group = PostsViewsTests.another_group
        text_from_post = post.text
        group_from_post = post.group
        url = reverse(
            'post_edit',
            kwargs={'username': post.author.username, 'post_id': post.id}
        )
        form_data = {
            'text': 'some text text here',
            'group': another_group.id,

        }
        self.another_authorized_user.post(url, data=form_data, follow=True)
        PostsViewsTests.post.refresh_from_db()
        self.assertEqual(post.text, text_from_post)
        self.assertEqual(post.group, group_from_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        while Post.objects.all().count() < 13:
            Post.objects.create(
                text='some_text',
                author=cls.user,
                group=PaginatorViewsTest.group
            )

    def setUp(self):
        cache.clear()
        self.authorized_user = Client()
        self.authorized_user.force_login(PaginatorViewsTest.user)

    def test_index_paginator(self):
        response = self.authorized_user.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)
        response = self.authorized_user.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_group_posts_paginator(self):
        link = reverse('group_posts', kwargs={'slug': 'test_slug'})
        response = self.authorized_user.get(link)
        self.assertEqual(len(response.context.get('page').object_list), 10)
        response = self.authorized_user.get(
            reverse('group_posts', kwargs={'slug': 'test_slug'}) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_profile_test_index_paginator(self):
        user = PaginatorViewsTest.user
        link = reverse(
            'profile',
            kwargs={'username': user.username}
        )
        response = self.authorized_user.get(link)
        self.assertEqual(len(response.context.get('page').object_list), 10)
