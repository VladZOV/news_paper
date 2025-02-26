from datetime import datetime

from django.utils import timezone

from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, TemplateView

from .filters import PostFilter
from .forms import PostForm, BaseRegisterForm
from .models import Post, Category, PostCategory


class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = ['-created_at']
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        # К словарю добавим текущую дату в ключ 'time_now'.
        context['time_now'] = datetime.utcnow()
        # Добавим ещё одну пустую переменную,
        # чтобы на её примере рассмотреть работу ещё одного фильтра.
        context['next_sale'] = None

        return context

    @method_decorator(cache_page(60))  # кэш на 1 минуту для главной страницы
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'

    @method_decorator(cache_page(300))  # кэш на 5 минут для страницы поста
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Кэширование объекта поста/статьи
        cache_key = f'post_detail_{self.kwargs["pk"]}'
        post = cache.get(cache_key)

        if post is None:
            post = super().get_object(queryset)

            cache.set(cache_key, post, None)

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments_key = f'post_comments_{self.object.pk}'
        context['comments'] = cache.get(comments_key)

        if context['comments'] is None:
            context['comments'] = self.object.comments.all()
            cache.set(comments_key, context['comments'], None)

        return context


class PostSearchView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    @method_decorator(cache_page(300))  # кэш на 5 минут для поиска
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin,  CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_create.html'
    success_url = reverse_lazy('post_list')
    login_url = reverse_lazy('account_login')
    permission_required = 'post_news.add_post'
    raise_exception = True

    def form_valid(self, form):

        today = timezone.now().date()
        news_count = Post.objects.filter(
            author=self.request.user,
            created_at__date=today,
            post_type=Post.NEWS
        ).count()

        if news_count >= 3:
            raise ValidationError('Вы не можете публиковать более трех новостей в день.')

        if 'news/create' in self.request.path:
            form.instance.post_type = Post.NEWS
        elif 'articles/create' in self.request.path:
            form.instance.post_type = Post.ARTICLE

        response = super().form_valid(form)

        cache.delete_pattern('post_list_*')
        cache.delete_pattern('search_results_*')

        return response


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')
    login_url = reverse_lazy('account_login')
    permission_required = 'post_news.change_post'
    raise_exception = True

    def form_valid(self, form):

        old_post = self.get_object()

        response = super().form_valid(form)

        cache_key = f'post_detail_{self.object.pk}'
        cache.delete(cache_key)

        cache.delete_pattern(f'post_comments_{self.object.pk}')
        cache.delete_pattern('post_list_*')
        cache.delete_pattern('search_results_*')

        return response


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    login_url = reverse_lazy('account_login')
    permission_required = 'post_news.delete_post'
    raise_exception = True

    def post(self, request, *args, **kwargs):

        post = self.get_object()

        response = super().post(request, *args, **kwargs)
        cache_key = f'post_detail_{post.pk}'
        cache.delete(cache_key)

        cache.delete_pattern(f'post_comments_{post.pk}')
        cache.delete_pattern('post_list_*')
        cache.delete_pattern('search_results_*')

        return response


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post_categories = PostCategory.objects.filter(category=self.object)

        news = Post.objects.filter(
            postcategory__category=self.object,
            post_type=Post.NEWS
        )

        articles = Post.objects.filter(
            postcategory__category=self.object,
            post_type=Post.ARTICLE
        )

        context['news'] = news
        context['articles'] = articles

        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    @method_decorator(cache_page(600))  # кэш на 10 минут для списка категорий
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.subscribers.add(request.user)
    return redirect('category_detail', category_id=category.id)
