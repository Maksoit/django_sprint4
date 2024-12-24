"""
Добавил новые пути в соответсвии с заданием.
Добавлен аналог декоратора @login_required, только теперь для CBV.
(Дополнительная проверка не повредит).
Переписаны прошлые вьюшки под классы.
"""
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'blog'

urlpatterns = [
    path(
        "",
        views.IndexListView.as_view(),
        name="index",
    ),
    path(
        "posts/<int:post_id>/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryListView.as_view(),
        name="category_posts",
    ),
    path(
        'posts/create/',
        login_required(views.PostCreateView.as_view()),
        name='create_post',
        ),
    path(
        'posts/<int:post_id>/edit/',
        login_required(views.PostUpdateView.as_view()),
        name='edit_post',
        ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        login_required(views.CommentUpdateView.as_view()),
        name='edit_comment'),
    path(
        'posts/<int:post_id>/delete/',
        login_required(views.PostDeleteView.as_view()),
        name='delete_post'),
    path(
        'profile/edit/',
        login_required(views.ProfileUpdateView.as_view()),
        name='edit_profile'),
    path(
        'profile/<str:username>/',
        (views.ProfileListView.as_view()),
        name='profile'),
    path(
        'posts/<int:post_id>/add_comment/',
        login_required(views.CommentCreateView.as_view()),
        name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        login_required(views.CommentUpdateView.as_view()),
        name='edit_comment'),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        login_required(views.CommentDeleteView.as_view()),
        name='delete_comment'),
]
