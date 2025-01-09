from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Post


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        subscribers = User.objects.filter(subscribed_categories__in=instance.categories.all()).distinct()

        for user in subscribers:
            subject = f'Новая новость: {instance.title}'
            message = render_to_string('email_template.html', {
                'username': user.username,
                'title': instance.title,
                'preview': instance.text[:50]
            })
            send_mail(subject, message, 'my_mail@mail.ru', [user.email])
