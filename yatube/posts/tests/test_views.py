import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        super().setUpClass()
        cls.user = User.objects.create_user(username='axx')
        cls.user2 = User.objects.create_user(username='oxx')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.user = TaskPagesTests.user
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.user2 = TaskPagesTests.user2
        self.authorized_client2.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'axx'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_image_0, self.post.image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_image_0, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'axx'}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_image_0, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        first_object = response.context['post']
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_image_0, self.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_add_comment(self):
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': 1}),
            {'text': "няшечка"})
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertContains(response, 'няшечка')
        self.authorized_client.logout()
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': 1}),
            {'text': "какашечка"})
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertNotContains(response, 'какашечка')

    def test_index_cache(self):
        """ Тест кэширования
        """
        posts_content = self.authorized_client.get(
            reverse('posts:index')).content
        Post.objects.create(
            text='Testing cache text',
            author=self.user,
        )
        posts_cached = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(
            posts_content,
            posts_cached,
            'В кэш не было записи')
        cache.clear()
        posts_non_cached = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(
            posts_content,
            posts_non_cached,
            'Кэш не очищен')

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_add_follow(self):
        """
        проверяем что никто не подписан,
        потом подписываемся,
        потом удаляем
        """

        # проверяем, что authorized_client2 еще не подписан на автора поста
        response_1 = self.authorized_client2.get(reverse('posts:follow_index'))
        page_object_1 = response_1.context['page_obj'].object_list
        self.assertEqual((len(page_object_1)), 0)

        # подписываемся на автора поста
        self.authorized_client2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        # проверяем, что authorized_client2 подписался
        response_2 = self.authorized_client2.get(reverse('posts:follow_index'))
        page_object_2 = response_2.context['page_obj'].object_list
        self.assertEqual((len(page_object_2)), 1)

    def test_unfollow(self):
        self.authorized_client2.get(
            reverse('posts:profile_follow', kwargs={
                    'username': self.post.author})
        )

        response_1 = self.authorized_client2.get(reverse('posts:follow_index'))
        page_object_1 = response_1.context['page_obj'].object_list

        self.assertEqual((len(page_object_1)), 1)

        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={
                    'username': self.post.author})
        )

        response_2 = self.authorized_client2.get(reverse('posts:follow_index'))
        page_object_2 = response_2.context['page_obj'].object_list
        self.assertEqual((len(page_object_2)), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='axx')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        obj = Post(author=cls.user, text='Тестовый пост', group=cls.group)
        Post.objects.bulk_create([obj for i in range(13)])

    def setUp(self):
        self.authorized_client = Client()
        self.user = PaginatorViewsTest.user
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'axx'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'axx'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
