from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
# Импортируем созданное нами представление
from .views import PostList, PostDetail, PostSearchView, PostCreateView, PostUpdateView, PostDeleteView, \
    BaseRegisterView, upgrade_me, CategoryListView, CategoryDetailView, subscribe_to_category

urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', PostList.as_view(), name='post_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', PostDetail.as_view(), name='post_detail'),
   path('search/', PostSearchView.as_view(), name='post_search'),
   path('news/create/', PostCreateView.as_view(), name='news_create'),
   path('articles/create/', PostCreateView.as_view(), name='articles_create'),
   path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
   path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
   path('login/',
        LoginView.as_view(template_name='post_news/login.html'),
        name='login'),
   path('logout/',
        LogoutView.as_view(template_name='post_news/logout.html'),
        name='logout'),
   path('login/signup/',
        BaseRegisterView.as_view(template_name='post_news/signup.html'),
        name='signup'),
   path('upgrade/', upgrade_me, name='upgrade'),
   path('categories/', CategoryListView.as_view(), name='category_list'),
   path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
   path('subscribe/<int:category_id>/', subscribe_to_category, name='subscribe'),
]
