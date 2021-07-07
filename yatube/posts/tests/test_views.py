from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(slug='test-slug',)
        cls.user = User.objects.create_user(username='Weigo')
        cls.post = Post.objects.create(text='Тестовый пост', author=cls.user,
                                       group=cls.group)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': 'test-slug'}),
            'new_post.html': reverse('new_post')}
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group_posts', kwargs={
            'slug': 'test-slug'}))
        test_group = response.context['group']
        test_post = response.context['page'][0]
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, self.post)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон создания нового поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        test_post = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in test_post.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': self.post.id}))
        test_post_edit = {
            'text': forms.fields.CharField}
        for value, expected in test_post_edit.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон страницы профайла пользователя
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': self.user.username}))
        profile = {
            'author': self.post.author}
        for value, expected in profile.items():
            with self.subTest(value=value):
                post_author = response.context[value]
                self.assertEqual(post_author, expected)
        test_post = response.context['page'][0]
        self.assertEqual(test_post, self.user.posts.all()[0])

    def test_check_post_shows_in_correct_group(self):
        """Пост не попадает в группу, для которой не был предназначен."""
        response = self.authorized_client.get(reverse('index'))
        test_post = response.context['page'][0]
        test_group = test_post.group
        self.assertEqual(test_group, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Weigo123')
        cls.group = Group.objects.create(slug='test-slug')
        for count in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост номер {count}',
                author=cls.user,
                group=cls.group)

        cls.templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': cls.group.slug}),
            'profile.html': reverse('profile',
                                    kwargs={'username': cls.user.username})}

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """На главной странице, странице группы и на странице
        профайла пользователя паджинатор выводит 10 постов"""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context.get(
                    'page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """На главной странице, странице группы и на странице
        профайла пользователя паджинатор еще 3 поста"""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(
                    response.context.get('page').object_list), 3)


class Cache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Weigo12345')
        cls.group = Group.objects.create(slug='test-slug')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        Post.objects.create(author=self.user,
                            text='Тестовый пост',
                            group=self.group)
        self.authorized_client.get(reverse('index'))
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context, None)
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(response.context, None)
        self.assertEqual(response.context['page'][0].text, 'Тестовый пост')
