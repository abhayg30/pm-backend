from django.db import models
from auths.models import User
import datetime

class ExperienceDetails(models.Model):
    
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField(null = True)
    company = models.CharField(max_length = 255)
    description = models.CharField(max_length = 2000)
    title = models.CharField(max_length = 255)

    REQUIRED_FIELDS = ['user', 'from_date', 'company', 'description', 'title']
