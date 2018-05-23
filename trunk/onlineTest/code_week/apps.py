from django.apps import AppConfig

class CodeWeekConfig(AppConfig):
    name = 'code_week'
    def ready(self):
        from code_week.models import ProblemCategory
        categorys = ProblemCategory.objects.all()

        nowSet = set()
        for catgory in categorys:
            nowSet.add(catgory.category)

        shouldList = ['C', 'C++', 'Python', 'Java']
        shouldSet = set(shouldList)
        shouldAddSet = shouldSet - nowSet
        for toAddCategory in shouldAddSet:
            ProblemCategory.objects.create(category=toAddCategory)