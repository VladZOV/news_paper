from django.contrib import admin

from .models import Author, Category, Post

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Author)