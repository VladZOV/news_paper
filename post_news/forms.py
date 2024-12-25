from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['author', 'title', 'text',]

    def save(self, commit=True, post_type=None):
        instance = super().save(commit=False)
        if post_type:
            instance.post_type = post_type
        if commit:
            instance.save()
        return instance
