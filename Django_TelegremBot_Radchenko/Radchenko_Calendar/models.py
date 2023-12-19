from django.db import models

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=255)
    details = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()

class BotStatistics(models.Model):
    date = models.DateField()
    user_count = models.PositiveIntegerField()
    event_count = models.PositiveIntegerField()
    edited_events = models.PositiveIntegerField()
    cancelled_events = models.PositiveIntegerField()