from django.db import models
from auths.models import User
from progression.progresslogs.models import ProgressLogDetails
from industry.models import JobDescription

class CommentLogDetails(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    progLogParent = models.ForeignKey(ProgressLogDetails, on_delete = models.CASCADE)
    commentDescription = models.CharField(max_length = 2000, blank = True, default = '')
    dateEntry = models.DateTimeField(auto_now_add = True)
    job = models.ForeignKey(JobDescription, on_delete = models.CASCADE)

    REQUIRED_FIELDS = ['user', 'dateEntry', 'job', 'progLogParent', 'commentDescription']