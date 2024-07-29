from django.db import models
from auths.models import User

class ProjectDetails(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 255)
    description = models.CharField(max_length = 2000, blank = True, default = '')
    from_date = models.DateField(null = True)
    to_date = models.DateField(null = True)




    REQUIRED_FIELDS = ['user' , 'name']