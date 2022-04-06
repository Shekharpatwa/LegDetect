from django.db import models
from django.contrib.auth.models import User


# Create your models here.
#For Forget token user profile
# class Profile(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE)
#     forget_token = models.CharField(max_length=1000)

class Prof(models.Model):
    user = models.CharField(max_length=255)
    forget_token = models.CharField(max_length=1000)


# For Storing user Results of Live Detection
class ImageRes(models.Model):
    name = models.CharField(max_length=255)
    ImgLeftAngle = models.CharField(max_length=255)
    ImgRightAngle = models.CharField(max_length=255)
    date = models.DateField()

class LiveRes(models.Model):
    name = models.CharField(max_length=255)
    LiveLeftAngle = models.CharField(max_length=255)
    LiveRightAngle = models.CharField(max_length=255)
    date = models.DateField()