from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем ее в качестве переменной класса
        cls.user = User.objects.create_user(username='testuser')
        cls.text = 'Пост длиной более 15 символов'
        cls.post = Post.objects.create(text=cls.text, author=cls.user)
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы', slug='slug')

    def test_object_name_is_title_field(self):
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_object_name_title_have_15_symbols(self):
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
