from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

from .models import Post, PostCategory, Category


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'post_type',
            'author'
        ]

    def save(self, commit=True):
        # Сохраняем пост
        instance = super().save(commit=False)

        if commit:
            instance.save()

        # Очищаем существующие связи
        PostCategory.objects.filter(post=instance).delete()

        # Создаем новые связи с категориями
        for category in self.cleaned_data['categories']:
            PostCategory.objects.create(
                post=instance,
                category=category
            )

        return instance


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
