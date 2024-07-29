from django.db import models
from auths.models import User


class PartnerDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    company = models.CharField(max_length=255)

    REQUIRED_FIELDS = ["user", "company"]


class JobDescription(models.Model):
    class JobStatus(models.TextChoices):
        NOT_STARTED = 0
        IN_PROGRESS = 1
        FINISHED = 2

    job_posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    skills_req = models.CharField(max_length=2000)
    short_description = models.CharField(max_length=1000)
    description = models.CharField(max_length=7000)
    vacancies = models.IntegerField()
    location = models.CharField(max_length=255)
    other_req = models.CharField(max_length=2000)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    closes_at = models.DurationField()
    is_active = models.IntegerField()
    job_status = models.IntegerField(
        choices=JobStatus.choices, default=JobStatus.NOT_STARTED
    )

    def __str__(self):
        return str(self.created_at)

    REQUIRED_FIELDS = [
        "position",
        "skills_req",
        "description",
        "vacancies",
        "location",
        "closes_at",
        "is_active",
        "company",
        "short_description",
        "category",
        "job_status",
    ]
