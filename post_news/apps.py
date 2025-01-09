from django.apps import AppConfig


class PostConfig(AppConfig):
    name = 'post_news'

    def ready(self):
        import post_news.signals
