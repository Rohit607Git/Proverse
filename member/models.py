from django.db import models
from account.models import User
from stage.models import Project

class Invite(models.Model):
    STATUS_CHOICES = (
        ('Invited', 'Invited'),
        ('Requested','Requested'),
        ('Rejected', 'Rejected'),)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sent_invites')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='received_invites')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
