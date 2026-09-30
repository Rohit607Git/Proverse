from django.db import models
from account.models import User

class Project(models.Model):
    STATUS_CHOICES=(('Public','Public'),('Private','Private'))
    id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=255, unique=True)
    description=models.TextField(null=False)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Public',null=False)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='created_projects')
    start_date=models.DateField(null=False)
    end_date=models.DateField(null=False)

class Task(models.Model):
    STATUS_CHOICES = (
        ('ToDo', 'ToDo'),
        ('InProgress', 'InProgress'),
        ('Done', 'Done'))
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'))
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey("member.Team", on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=11, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    due_date = models.DateField()
