import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from .tasks import send_weekly_newsletter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),  # понедельник в 8:00
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_newsletter'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
