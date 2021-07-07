import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, User

TEMP_MEDIA = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Weigo')
        cls.group = Group.objects.create(title='test_group', slug='test-slug')
        cls.post = Post.objects.create(text='Тестовый пост', author=cls.user,
                                       group=cls.group)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_created(self):
        """При отправке формы создаётся новая запись в базе данных"""
        posts_count = Post.objects.count()
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
            content_type='image/gif')

        form_data = {
            'text': 'Текст тестового поста',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='Текст тестового поста',
                                            group=self.group,
                                            image='posts/small.gif').exists())
        self.assertTrue(response.context['page'][0].image.name, uploaded.name)

    def test_post_correct_edit(self):
        """При редактировании поста через форму на странице
        изменяется соответствующая запись в базе данных"""
        form_data = {
            'text': 'Текст тестового поста отредактированный',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}), data=form_data)
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.user.username,
                                    'post_id': self.post.id}))
        self.assertEqual(
            response.context['post'].text,
            'Текст тестового поста отредактированный')
        self.assertTrue(Post.objects.filter(
            text='Текст тестового поста отредактированный',
            group=self.group).exists())
