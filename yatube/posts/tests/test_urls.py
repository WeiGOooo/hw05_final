from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User
from django.core.cache import cache


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(slug='test-slug')
        cls.author = User.objects.create_user(username='WeiGO')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.post = Post.objects.create(
            author=cls.author, text='Тестовый текст', group=cls.group)
        cls.templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{cls.group.slug}/',
            'new_post.html': '/new/',
            'profile.html': f'/{cls.author.username}/',
            'post.html': f'/{cls.author.username}/{cls.post.id}/',
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.not_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_guest_client_url(self):
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                if adress == reverse('new_post'):
                    response = self.guest_client.get(adress)
                    self.assertEqual(response.status_code, 302)
                else:
                    response = self.guest_client.get(adress)
                    self.assertEqual(response.status_code, 200)
        response = self.guest_client.get(
            f'/{self.author.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_page_not_found(self):
        response = self.guest_client.get('/hsfhdbf/', follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')

    def test_author_client_url(self):
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_author.get(adress)
                self.assertEqual(response.status_code, 200)
        response = self.authorized_author.get(
            f'/{self.author.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_not_author_client_url(self):
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_not_author.get(adress)
                self.assertEqual(response.status_code, 200)
        response = self.authorized_not_author.get(
            f'/{self.author.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
