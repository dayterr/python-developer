from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест',
            slug='test-group',
            description='Это тестовая группа'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='Это текст тестового поста. Кстати, привет, мир!',
            group=cls.group,
            author=cls.user,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def check_post_correct_data(self, context, is_page):
        """Вспомогательный метод для проверки атрибутов поста."""
        if is_page:
            self.assertIn('page', context)
            post = context['page'].object_list[0]
        else:
            self.assertIn('post', context)
            post = context['post']
        self.assertEqual(PostsPagesTests.post.text, post.text)
        self.assertEqual(PostsPagesTests.post.group, post.group)
        self.assertEqual(PostsPagesTests.post.pub_date, post.pub_date)
        self.assertEqual(PostsPagesTests.post.author, post.author)

    def test_pages_correct_templates(self):
        templates_pages_names = (
            ('index.html', 'index', None),
            ('post.html', 'post', (PostsPagesTests.user.username,
                                   PostsPagesTests.post.id,)),
            ('group.html', 'group_view', (PostsPagesTests.group.slug,)),
            ('profile.html', 'profile', (PostsPagesTests.user.username,)),
            ('post_new.html', 'new_post', None),
            ('post_new.html', 'post_edit', (PostsPagesTests.user.username,
                                            PostsPagesTests.post.id,)),
        )
        for template, reverse_name, args in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse(reverse_name,
                                                              args=args))
                self.assertTemplateUsed(response, 'posts/' + template)

    def test_index_correct_context(self):
        response = self.client.get(reverse('index'))
        self.check_post_correct_data(response.context, True)

    def test_group_correct_context(self):
        response = self.client.get(reverse(
            'group_view', kwargs={'slug': PostsPagesTests.group.slug}
        ))
        self.assertIn('group', response.context)
        group_from_context = response.context['group']
        self.assertEqual(PostsPagesTests.group.title, group_from_context.title)
        self.assertEqual(PostsPagesTests.group.description,
                         group_from_context.description)
        self.check_post_correct_data(response.context, True)

    def test_group_unused_correct_context(self):
        group_unused = Group.objects.create(
            title='Контрольная',
            slug='test-unused'
        )
        response = self.client.get(reverse(
            'group_view', kwargs={'slug': group_unused.slug}
        ))
        self.assertIn('page', response.context)
        posts = response.context['page'].object_list
        self.assertNotIn(PostsPagesTests.post, posts)

    def test_profile_correct_context(self):
        response = self.client.get(reverse(
            'profile', kwargs={
                'username': PostsPagesTests.user.username,
            })
        )
        self.assertIn('author', response.context)
        self.assertEqual(PostsPagesTests.user, response.context['author'])
        self.check_post_correct_data(response.context, True)

    def test_post_correct_context(self):
        response = self.client.get(reverse(
            'post', kwargs={
                'username': PostsPagesTests.post.author,
                'post_id': PostsPagesTests.post.id,
            })
        )
        self.assertIn('author', response.context)
        self.assertEqual(PostsPagesTests.user, response.context['author'])
        self.check_post_correct_data(response.context, False)

    def test_paginator(self):
        objs = (Post(text=f'Какой-то пост {i}',
                     group=PostsPagesTests.group) for i in range(14))
        Post.objects.bulk_create(objs)
        all_posts = PostsPagesTests.group.posts.count()
        for page in range(1, 3):
            with self.subTest(page=page):
                response = self.client.get(reverse(
                    'group_view', args=[PostsPagesTests.group.slug]
                ), data={'page': page})
                self.assertIn('page', response.context)
                page_from_view = response.context['page']
                page_posts = page_from_view.object_list
                if page_from_view.has_next():
                    self.assertEqual(len(page_posts), settings.POSTS_PER_PAGE)
                else:
                    last_page = all_posts % settings.POSTS_PER_PAGE
                    self.assertEqual(len(page_posts), last_page)

    def test_new_post_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('is_new', response.context)
        self.assertIs(response.context['is_new'], True)

    def test_edit_post_correct_context(self):
        args = (PostsPagesTests.user.username, PostsPagesTests.post.id)
        response = self.authorized_client.get(reverse('post_edit', args=args))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('is_new', response.context)
        self.assertIsInstance(response.context['is_new'], bool)
        self.assertFalse(response.context['is_new'])
