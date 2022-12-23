from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import Resolver404, resolve

from posts.models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='axx')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user1 = TaskURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.user2 = User.objects.create_user(username='HasNoName')
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user2)

    def test_urls_anon(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test/',
            'posts/profile.html': '/profile/axx/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_404(self):
        """URL-адрес использует соответствующий шаблон."""
        address = '/blablabla/'
        with self.subTest(address=address), self.assertRaises(Resolver404):
            resolve(self.guest_client.get(address))

    def test_urls_auth(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/axx/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/axx/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists_at_desired_location(self):
        """Страница /posts/1/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anon_user(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_url_redirect_anon_user(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )

    def test_edit_url_redirect_another_user(self):
        """Страница по адресу /posts/1/edit/ перенаправит не автора
        поста на главную страницу.
        """
        response = self.authorized_client_other.get(
            '/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/'
        )

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/1/edit/ доступна авторизованному автору поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_non_existing_url(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.authorized_client.get('/balbalba/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
