import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        small_gif0 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded0 = SimpleUploadedFile(
            name='small0.gif',
            content=small_gif0,
            content_type='image/gif'
        )
        small_gif1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded1 = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif1,
            content_type='image/gif'
        )
        super().setUpClass()
        cls.user = User.objects.create_user(username='axx')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = TestCreateForm.user
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """Проверка формы создания нового поста"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст',
            'image': self.uploaded0,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'axx'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Текст',
            group=TestCreateForm.group,
            image='posts/small0.gif',
        ).exists())

    def test_guest_new_post(self):
        """Тест на неавторизованного юзера"""
        form_data = {
            'text': 'куку',
            'group': self.group.id
        }
        self.guest_client.post(reverse('posts:post_create'),
                               data=form_data,
                               follow=True)
        self.assertFalse(Post.objects.filter(
            text='куку').exists())

    def test_form_update(self):
        """
        Проверка редактирования поста через форму на странице
        """
        self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        form_data = {
            'group': self.group.id,
            'text': 'Текст1',
            'image': self.uploaded1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        self.assertTrue(Post.objects.filter(
            text='Текст1',
            group=TestCreateForm.group,
            image='posts/small1.gif',
        ).exists())
