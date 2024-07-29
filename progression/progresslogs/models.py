from django.db import models
from auths.models import User
from industry.models import JobDescription

class ProgressLogDetails(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    description = models.CharField(max_length = 2000, blank = True, default = '')
    dateEntry = models.DateTimeField(auto_now_add = True)
    job = models.ForeignKey(JobDescription, on_delete = models.CASCADE)

    REQUIRED_FIELDS = ['user', 'dateEntry', 'job', 'description']