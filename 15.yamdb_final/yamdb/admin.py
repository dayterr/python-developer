from django.contrib import admin

from .models import Category, Genre, Comment, Review, Title, User


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'title', 'pub_date', 'author', 'score', )
    list_filter = ('title', )
    search_fields = ('text', )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'year', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'review', 'pub_date', 'author', )
    list_filter = ('review', )
    search_fields = ('text', )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'bio', 'role')
    search_fields = ('username',)
    list_filter = ('date_joined',)
    empty_value_display = '-пусто-'
