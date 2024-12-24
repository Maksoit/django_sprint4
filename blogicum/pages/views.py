"""Добавлены вьюшки для отображения кастомных страниц ошибок."""
from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Возвращает кастомную страниццу 404."""
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем.
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Возвращает кастомную страницу 403."""
    return render(request, 'pages/403csrf.html', status=403)


def failure_500(request, *args):
    """Возвращает кастомную страницу 500."""
    return render(request, 'pages/500.html', status=500)
