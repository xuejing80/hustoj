from django.db import models

# Create your models here.

class faqs(models.Model):
    """
    问答对表
    """
    id = models.AutoField(primary_key=True)
    question_content = models.TextField()
    answer_content = models.TextField()
    question_keywork = models.CharField(max_length=50)

    def __str__(self):
        return str(self.id)
