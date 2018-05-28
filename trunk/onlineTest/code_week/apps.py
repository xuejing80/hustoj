from django.apps import AppConfig
from django.db import transaction

class CodeWeekConfig(AppConfig):
    name = 'code_week'
    def ready(self):
        from code_week.models import ProblemCategory
        try:
            with transaction.atomic():
                categorys = ProblemCategory.objects.all()

                nowSet = set()
                for catgory in categorys:
                    nowSet.add(catgory.category)

                shouldList = ['C', 'C++', 'Python', 'Java']
                shouldSet = set(shouldList)
                shouldAddSet = shouldSet - nowSet
                for toAddCategory in shouldAddSet:
                    ProblemCategory.objects.create(category=toAddCategory)
        except:
            pass