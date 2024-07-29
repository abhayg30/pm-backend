from django.db import models
from auths.models import User


class Education(models.Model):
    POSTGRADUATE = "PG"
    UNDERGRADUATE = "UG"
    DIPLOMA = "DP"
    DOCTORATE = "PD"
    DEGREE_TYPES = [
        (POSTGRADUATE, "Postgraduate"),
        (UNDERGRADUATE, "Undergraduate"),
        (DIPLOMA, "Diploma"),
        (DOCTORATE, "PD")
    ]
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    university = models.CharField(max_length = 255)
    degree_type = models.CharField(max_length = 2, choices = DEGREE_TYPES)
    stream = models.CharField(max_length = 255)
    from_date = models.DateField()
    to_date = models.DateField(null = True)
    specializaion = models.CharField(max_length = 255, blank = True, default = '')

    REQUIRED_FIELDS = ['user', 'university', 'degree_type', 'from_date']
# Create your models here.
