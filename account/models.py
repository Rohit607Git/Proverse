from django.db import models

class User(models.Model):
    GENDER_CHOICES = (('M', 'Male'),('F', 'Female'),('O', 'Other'),)
    fullname = models.CharField(max_length=150,null=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    role = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)