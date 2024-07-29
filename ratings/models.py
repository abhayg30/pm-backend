from django.db import models
from auths.models import User

class RatingDetails(models.Model):
    user = models.ForeignKey(User, related_name='ratedBy', on_delete = models.CASCADE)
    ratingOn = models.ForeignKey(User, related_name='ratingOn', on_delete = models.CASCADE)
    description = models.CharField(max_length = 2000, blank = True, default = '')
    dateEntry = models.DateTimeField(auto_now_add = True)
    overall = models.IntegerField()
    deliverables = models.IntegerField()
    communication = models.IntegerField()

    REQUIRED_FIELDS = ['user', 'dateEntry', 'overall', 'description', 'deliverables','communication']