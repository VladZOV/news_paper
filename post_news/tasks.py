from django.utils import timezone
from .models import Post, User, Category
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string


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


@shared_task
def send_post_notification(post_id):
    post = Post.objects.get(id=post_id)

    subscribers = User.objects.filter(
        subscribed_categories__in=post.categories.all()
    ).distinct()

    for user in subscribers:
        subject = f'Новый пост: {post.title}'
        message = render_to_string('email_template.html', {
            'username': user.username,
            'post_title': post.title,
            'post_preview': post.preview(),
        })

        send_mail(
            subject,
            message,
            'my_mail@mail.ru',
            [user.email]
        )


@shared_task
def send_weekly_digest():

    last_week_posts = Post.objects.filter(
        created_at__week=timezone.now().isocalendar()[1]
    )

    users = User.objects.all()

    for user in users:

        user_categories = user.subscribed_categories.all()

        user_posts = last_week_posts.filter(categories__in=user_categories)

        if user_posts.exists():
            subject = 'Еженедельный дайджест новостей'
            message = render_to_string('email_template.html', {
                'username': user.username,
                'posts': user_posts
            })

            send_mail(
                subject,
                message,
                'my_mail@mail.ru',
                [user.email]
            )
