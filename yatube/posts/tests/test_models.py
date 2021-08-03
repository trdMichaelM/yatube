from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='p' * 200,
            slug='test_slug',
            description='test_description'
        )

    def test_text_title(self):
        group = GroupModelTest.group
        expected_title = group.title
        self.assertEqual(expected_title, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            text=('Ветер веет с юга\n'
                  'И луна взошла,\n'
                  'Что же ты, б*ядюга,\n'
                  'Ночью не пришла?\n'
                  'Не пришла ты ночью,\n'
                  'Не явилась днем.\n'
                  'Думаешь, мы др*чим?\n'
                  'Нет! Других е*ём!'),
            author=cls.user
        )

    def test_text_title(self):
        post = PostModelTest.post
        expected_title = post.text[:15]
        self.assertEqual(expected_title, str(post))
