from django.core.mail import send_mail
from django.utils import timezone
from .models import Post, User


def send_weekly_newsletter():
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    new_posts = Post.objects.filter(created_at__gte=one_week_ago)

    subscribers = User.objects.filter(is_subscribed=True)

    for user in subscribers:
        subject = 'Новые статьи за неделю'
        message = 'Вот новые статьи, добавленные за последнюю неделю:\n\n'

        for post in new_posts:
            message += f"{post.title} - {post.get_absolute_url()}\n"

        send_mail(subject, message, 'my_mail@mail.com', [user.email])
