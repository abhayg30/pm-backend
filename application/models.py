from django.db import models
from auths.models import User
from industry.models import JobDescription


class AppliedToJob(models.Model):
    CHOICES = [
        ("Not yet applied", "NA"),
        ("Under review", "UR"),
        ("Rejected", "RE"),
        ("Approved", "AP"),
        ("Withdrawn", "WD"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=CHOICES, default="NA")
    has_applied = models.BooleanField(default=False)
    has_accepted = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["user", "job"]


class MatchedJobs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=1000, default="")


# Create your models here.
