"""
Добавил модель Comment и модифицировал другие модели.
Часть моделей взял из своего 3 спринта.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

STRING_LENGTH = 25
User = get_user_model()


class BaseModel(models.Model):
    """
    Абстрактная модель, которая используется для моделей,
    которым нужны содержащиеся поля.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Модель для категорий, к которым могут принадлежать посты.
    Магический метод __str__ для правильного отображения.
    """

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')

    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
        max_length=128
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    """
    Модель для местоположений, к которым могут принадлежать посты.
    Магический метод __str__ для правильного отображения.
    """
    name = models.CharField(max_length=256, verbose_name='Название места')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(BaseModel):
    """
    Модель для публикаций в блоге.
    Кроме полей содержит связь с автором (1:1),
    категорией (1:1) и местоположением(1:1).
    """

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')

    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )

    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
    )

    category = models.ForeignKey(
        Category,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='posts'
    )

    image = models.ImageField('Фото', upload_to='post_images/', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail', args=[self.pk]
        )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)


class Comment(models.Model):
    """
    Модель для комментариев к публикациям.
    Связана с пользователем(1:1) и публикацией(1:1).
    """

    text = models.TextField('Текст комментария')

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        related_name='comments',
    )

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
