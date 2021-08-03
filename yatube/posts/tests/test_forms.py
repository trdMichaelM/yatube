import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()

TEST_DIR = 'test_data'


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')
        cls.test_post = Post.objects.create(
            text='test_text',
            author=cls.user
        )
        cls.test_group = Group.objects.create(
            title='Test group',
            slug='test_group_slug',
            description='test group description'
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_DIR)
        super().tearDownClass()

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_new_post(self):
        user = self.__class__.user
        posts_count = Post.objects.count()
        form_data = {
            'text': 'some text for test'
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=user,
                text='some text for test',
                group__isnull=True
            ).exists()
        )

    def test_create_new_post_with_image(self):
        """Проверяем, что при отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных.
        """
        user = self.__class__.user
        uploaded = self.__class__.uploaded
        posts_count = Post.objects.count()
        text = 'some text for test post with image'
        form_data = {
            'text': text,
            'image': uploaded
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=user,
                text=text,
                image='posts/image.gif',
                group__isnull=True
            ).exists()
        )

    def test_create_new_post_into_group(self):
        user = self.__class__.user
        posts_count = Post.objects.count()
        test_group_id = PostFormTest.test_group.id
        form_data = {
            'text': 'some text here',
            'group': test_group_id,
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=user,
                text='some text here',
                group=test_group_id
            ).exists()
        )

    def test_check_change_post(self):
        """Проверяем, что при редактировании поста через форму
        на странице /<username>/<post_id>/edit/ изменяется соответствующая
        запись в базе данных.
        """
        post = PostFormTest.test_post
        test_group = PostFormTest.test_group
        form_data = {
            'text': 'it\'s a new post',
            'group': test_group.id,
        }
        link = reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': post.id}
        )
        self.authorized_user.post(link, data=form_data, follow=True)
        PostFormTest.test_post.refresh_from_db()
        self.assertEqual(post.text, 'it\'s a new post')
        self.assertEqual(post.group, test_group)
