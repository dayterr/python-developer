from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        help_texts = {
            'group': 'Группа, к которой относится пост.',
            'text': 'Напишите текст, соответствующий тематике группы',
        }
