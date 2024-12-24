"""
Создал формы для поста, профиля и комментария.
Все формы связаны с соответствующими моделями.
"""
from django import forms
from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # Использован fields так как количество нужных полей меньше
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('author', 'post', 'created_at',)
