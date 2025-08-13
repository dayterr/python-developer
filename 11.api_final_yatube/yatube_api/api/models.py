from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название соообщества',
                             max_length=200)

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(Group, verbose_name='Сообщество',
                              on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='posts')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Пост',
    )
    text = models.TextField()
    created = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='Подписчик',
                             related_name='follower',
                             on_delete=models.CASCADE,
                             blank=True, null=True)
    following = models.ForeignKey(User, verbose_name='Подписант',
                                  related_name='following',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='Подписчик и подписант должны быть разными людьми')
        ]
