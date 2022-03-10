from django.db import models
from django.contrib.auth.models import User


# Create your models here.
#For Forget token user profile
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    forget_token = models.CharField(max_length=1000)

# For Storing user Results of Live Detection
class liveResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    LiveRes1 = models.CharField(max_length=255)
    LiveRes2 = models.CharField(max_length=255)
    date = models.DateField()

class imageResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imgRes1 = models.CharField(max_length=255)
    imgRes2 = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.name
    