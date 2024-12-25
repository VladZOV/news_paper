from django import forms
from django_filters import FilterSet, DateFilter, CharFilter

from .models import Post


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название новости'
    )

    author_name = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Имя автора'
    )

    created_after = DateFilter(
        field_name='created_at',
        lookup_expr='gt',
        label='Создана после',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['title', 'author_name', 'created_after']
