from django.db import models
from auths.models import User

class UploadResume(models.Model):
    uploaded_at = models.DateField(auto_now_add = True)
    resume = models.FileField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    REQUIRED_FIELDS = ['user', 'resume']

class ResumeData(models.Model):
    resume = models.ForeignKey(UploadResume, on_delete = models.CASCADE)
    url = models.CharField(max_length = 3000)

    REQUIRED_FIELDS = ['resume', 'url']
