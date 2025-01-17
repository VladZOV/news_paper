from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .tasks import send_post_notification


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)

    def update_rating(self):
        # Рейтинг статей автора * 3
        post_rating = self.post_set.aggregate(
            post_rating=models.Sum('rating')
        )['post_rating'] * 3 or 0

        # Рейтинг комментариев автора
        comment_rating = Comment.objects.filter(
            user=self.user
        ).aggregate(
            comment_rating=models.Sum('rating')
        )['comment_rating'] or 0

        # Рейтинг комментариев к статьям автора
        post_comment_rating = Comment.objects.filter(
            post__author=self
        ).aggregate(
            post_comment_rating=models.Sum('rating')
        )['post_comment_rating'] or 0

        # Обновление общего рейтинга
        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    NEWS = 'NW'
    ARTICLE = 'AR'
    POST_TYPES = [
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=NEWS)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.text[:124]}..." if len(self.text) > 124 else self.text

    def __str__(self):
        return self.title

    def notify_subscribers(self):
        for subscriber in self.categories.values_list('subscribers', flat=True):
            user = User.objects.get(id=subscriber)
            subject = self.title
            message = render_to_string('email_template.html', {
                'username': user.username,
                'title': self.title,
                'preview': self.text[:50]  # первые 50 символов текста
            })
            send_mail(subject, message, 'from@example.com', [user.email])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        self.notify_subscribers()
        if is_new:
            # Асинхронная отправка уведомлений
            send_post_notification.delay(self.id)


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
