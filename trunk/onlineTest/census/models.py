from django.db import models

# Create your models here.


class Census(models.Model):
    registered_users = models.IntegerField()
    choices = models.IntegerField()
    programms = models.IntegerField()
    fills = models.IntegerField()
    homework = models.IntegerField()
    save_time = models.DateField()

class Weights(models.Model):
    pythons = models.IntegerField()
    javas = models.IntegerField()
    cpps = models.IntegerField()
    begins = models.IntegerField()
    advances = models.IntegerField()
    savetime = models.DateField()