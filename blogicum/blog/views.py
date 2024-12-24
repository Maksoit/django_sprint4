"""
Все вью функции переписаны на CBV, так как это удобный инструмент,
о котором нам рассказали в курсе.
Для редиректа используется reverse_lazy вместо reverse для избежания ошибок.
Добавлены оптимизации запросов к БД.
Добавлен LoginRequiredMixin, так как декоратор нельзя использовать с CBV.
"""
from django.shortcuts import get_object_or_404, redirect
from blog.models import Category, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from .forms import PostForm, ProfileForm, CommentForm
from .models import Comment, User
from django.utils import timezone
from django.db.models import Count


POSTS_PER_PAGE = 10


def filter_posts(
        posts=None,
        filter_flag=True,
        category_flag=None,
        author_flag=None):
    """Фильтрует посты на основе параметров фильтрации."""
    if posts is None:
        posts = Post.objects.all()

    queryset = posts.prefetch_related(
        'comments'
    ).select_related(
        'location', 'category', 'author',
    )

    if filter_flag:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    if category_flag:
        queryset = queryset.filter(category=category_flag)

    if author_flag:
        queryset = queryset.filter(author=author_flag)

    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by(Post._meta.ordering[0])


class IndexListView(ListView):
    """
    CBV для главной страницы блога.
    Отвечает за список постов с пагинацией (под капотом).
    Фильтрует посты с помощью функции `filter_posts`,
    чтобы показать только нужные записи.
    """

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        """Возвращает отфильтрованный список постов."""
        return filter_posts(Post.objects)


class PostDetailView(DetailView):
    """
    CBV для страницы конкретного поста.
    Показывает подробную информацию о посте, включая комментарии
    и форму для добавления комментариев
    (Нужная информация включена в контекст).
    """

    model = Post
    template_name = 'blog/detail.html'
    paginate_by = POSTS_PER_PAGE
    pk_url_kwarg = 'post_id'

    def get_object(self):
        """
        Получает объект поста по его ID.
        Если текущий пользователь не является автором,
        будет возвращен пост для общего доступа.
        """
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            post = get_object_or_404(
                filter_posts(Post.objects),
                pk=self.kwargs[self.pk_url_kwarg],
            )
        return post

    def get_context_data(self, **kwargs):
        """Добавляет форму комментария и список комментариев в контекст."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryListView(ListView):
    """
    CBV для отображения постов в определенной категории.
    Фильтрует посты по переданной категории и отображает их.
    Пагинация под капотом.
    """

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE
    pk_url_kwarg = 'category_slug'

    def get_queryset(self):
        """Получает все посты из конкретной категории, которые опубликованы."""
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs[self.pk_url_kwarg]
        )
        return filter_posts(category.posts.all())

    def get_context_data(self, **kwargs):
        """Добавляет информацию о категории в контекст."""
        context = super().get_context_data(**kwargs)
        # Добавляем категорию в контекст
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs[self.pk_url_kwarg]
        )
        context['category'] = category
        return context


class ProfileListView(ListView):
    """
    CBV для профиля пользователя.
    Показывает все посты, написанные пользователем,
    включая снятые с публикации.
    Пагинация под капотом.
    """

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_user(self):
        """Получает пользователя по его имени пользователя (username)."""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        """
        Получает все посты пользователя и фильтрует их,
        если текущий пользователь не является этим пользователем,
        с помощью функции filter_posts.
        """
        user = self.get_user()
        return filter_posts(
            user.posts.all(),
            self.request.user != user
        )

    def get_context_data(self, **kwargs):
        """Добавляет информацию о профиле пользователя в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    CBV для обновления профиля пользователя.
    Позволяет пользователю редактировать свой профиль.
    """

    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        """
        Получает объект пользователя
        (текущего авторизованного пользователя).
        """
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(username=self.request.user.username)

    def get_success_url(self):
        """Возвращает URL для редиректа после успешного обновления профиля."""
        return reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    CBV для создания нового поста.
    Создает новый пост, привязывая его к авторизованному пользователю.
    После успеха перенапрявляет на профиль автора.
    """

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        """Устанавливает автора поста перед сохранением."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращает URL для редиректа после успешного создания поста."""
        return reverse_lazy(
            'blog:profile', args=[self.request.user.username]
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    CBV для создания комментария к посту.
    Комментарий привязывается к конкретному посту и пользователю.
    """

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        """Устанавливает автора и пост для комментария перед сохранением."""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        """
        Возвращает URL для редиректа после
        успешного создания комментария.
        """
        return reverse_lazy(
            'blog:post_detail',
            args=[self.kwargs[self.pk_url_kwarg]])


class CommentUpdateDeleteMixin():
    """
    Миксин для обновления и удаления комментариев.
    Используется как для обновления, так и для удаления комментариев.
    Удобно использовать, соблюдается принцип DRY.
    """

    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        """
        Получает комментарий по его ID,
        если он принадлежит текущему пользователю.
        """
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )
        return comment

    def get_success_url(self):
        """
        Возвращает URL для редиректа после успешного
        изменения или удаления комментария.
        """
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])


class CommentUpdateView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin,
                        UpdateView):
    """
    CBV для обновления комментария.
    Позволяет пользователю редактировать свой комментарий.
    """

    form_class = CommentForm


class CommentDeleteView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin,
                        DeleteView):
    """
    CBV для удаления комментария.
    Удаляет комментарий, если он принадлежит текущему пользователю.
    """

    pass


class PostUpdateDeleteMixin():
    """
    Миксин для обновления и удаления постов.
    Проверяет, является ли пользователь автором поста,
    перед выполнением действий.
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет, является ли текущий пользователь автором поста.
        Если нет, перенаправляет на страницу поста.
        """
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostUpdateDeleteMixin, LoginRequiredMixin, UpdateView):
    """
    CBV для редактирования поста.
    Позволяет автору поста редактировать его.
    """

    form_class = PostForm


class PostDeleteView(PostUpdateDeleteMixin, LoginRequiredMixin, DeleteView):
    """
    CBV для удаления поста.
    Удаляет пост, если он принадлежит текущему пользователю.
    """

    def get_context_data(self, **kwargs):
        """Добавляет форму для подтверждения удаления в контекст."""
        return dict(
            **super().get_context_data(**kwargs),
            form=PostForm(instance=self.object),
        )

    def get_success_url(self):
        """Возвращает URL для редиректа после успешного удаления поста."""
        return reverse_lazy(
            'blog:profile', args=[self.request.user.username]
        )
