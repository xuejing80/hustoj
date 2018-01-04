from django.db import models

# Create your models here.

class Ansdb(models.Model):
    id = models.AutoField(primary_key=True)
    problem_id = models.IntegerField(null=False, verbose_name='编程题序号')
    language = models.IntegerField(null=False, verbose_name='编程题语言')
    tokens = models.TextField(null=False, verbose_name="编程答案标记")
	