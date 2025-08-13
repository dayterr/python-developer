from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True, verbose_name='О себе')
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=USER)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Genre(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveSmallIntegerField(
        db_index=True,
        validators=(validate_year,)
    )
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True)
    category = models.ForeignKey(Category, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name='titles', null=True)

    class Meta:
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'
        ordering = ('-year',)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        verbose_name='Рецензия',
        help_text='Введите текст рецензии')

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Название', related_name="reviews")

    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True, db_index=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор',
        related_name="reviews")

    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка', help_text="оцените от 1 до 10")

    class Meta:
        verbose_name = 'Рецензия'
        verbose_name_plural = 'Рецензии'
        unique_together = ('title', 'author', )
        constraints = [models.UniqueConstraint(fields=['title', 'author'],
                       name='OneAuthorForReview')]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name="comments")
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Рецензия')
    text = models.TextField(verbose_name='Комментарий')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
