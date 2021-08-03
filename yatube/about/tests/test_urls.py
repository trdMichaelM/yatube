from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_for_guest_client(self):
        """Тест страница /about/author/ доступны
        неавторизованному пользователю.
        """
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_for_guest_client(self):
        """Тест страница /about/tech/ доступны
        неавторизованному пользователю.
        """
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
