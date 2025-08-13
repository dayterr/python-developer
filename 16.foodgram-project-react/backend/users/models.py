from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Subscribe(models.Model):
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
