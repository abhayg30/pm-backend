from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from industry.models import JobDescription
from django.db.models import F, ExpressionWrapper, fields
import logging

logger = logging.getLogger("django")


def handle(*args, **options):
    # Get the current date
    logger.info("cron was called")
    current_date = datetime.now()

    # Get all job descriptions that have expired
    expired_jobs = JobDescription.objects.annotate(
        datetime_plus_integer=ExpressionWrapper(
            F("created_at") + F("closes_at"), output_field=fields.DateTimeField()
        )
    ).filter(datetime_plus_integer__lt=current_date, is_active=1)

    logger.info("The list: ", expired_jobs)

    for job in expired_jobs:
        job.is_active = 0
        job.save()
    self.stdout.write(self.style.SUCCESS('Updated job statuses for expired jobs.'))
