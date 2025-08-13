from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест',
            slug='test-group',
        )
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Это текст тестового поста. Кстати, привет, мир!',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, PostCreateFormTests.group)
        self.assertEqual(post.author, PostCreateFormTests.user)

    def test_edit_post(self):
        other_group = Group.objects.create(
            title='Другое',
            slug='other-group',
        )
        post = Post.objects.create(
            text='Это текст тестового поста. Кстати, привет, мир!',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
        )
        post_amount = Post.objects.count()
        kwargs = {
            'username': PostCreateFormTests.user.username,
            'post_id': post.id,
        }
        text_to_insert = 'А это текст, на который нужно исправить'
        form_data = {
            'text': text_to_insert,
            'group': other_group.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=post.id)
        self.assertRedirects(response, reverse('post', kwargs=kwargs))
        self.assertEqual(Post.objects.count(), post_amount)
        self.assertEqual(post.text, text_to_insert)
        self.assertEqual(post.group, other_group)
        self.assertEqual(post.author, PostCreateFormTests.user)

    def test_new_unauth(self):
        post_amount = Post.objects.count()
        form_data = {
            'text': 'Пост, который не добавится',
            'group': PostCreateFormTests.group,
        }
        response = self.client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        rev_login = reverse('login')
        rev_new = reverse('new_post')
        self.assertEqual(Post.objects.count(), post_amount)
        self.assertRedirects(response, f'{rev_login}?next={rev_new}')

    def test_edit_post_non_author(self):
        reader = User.objects.create(username='mimokrokodil')
        reader_client = Client()
        reader_client.force_login(reader)
        post = Post.objects.create(
            text='Это текст тестового поста. Кстати, привет, мир!',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
        )
        text = 'Этот текст не появится в посте'
        form_data = {
            'text': text,
        }
        kwargs = {
            'username': PostCreateFormTests.user.username,
            'post_id': post.id,
        }
        response = reader_client.post(
            reverse('post_edit', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        post_to_check = Post.objects.get(id=post.id)
        self.assertRedirects(response, reverse('post', kwargs=kwargs))
        self.assertNotEqual(post_to_check.text, text)
