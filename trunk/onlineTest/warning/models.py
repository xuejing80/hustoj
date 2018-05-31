from django.db import models

# Create your models here.
class WarningData(models.Model):
	id = models.AutoField(primary_key=True)
	data = models.TextField(null=True)
	tid = models.CharField(max_length=40)
