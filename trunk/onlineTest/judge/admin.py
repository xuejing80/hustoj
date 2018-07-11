from django.contrib import admin

# Register your models here.
from judge.models import Problem, Solution, SourceCode, SourceCodeUser, KnowledgePoint1, KnowledgePoint2, ClassName, \
    ChoiceProblem, Compileinfo


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem_id', 'title', 'creater')


class SolutionAdmin(admin.ModelAdmin):
    list_display = ('solution_id', 'problem_id', 'in_date')


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(SourceCodeUser)
admin.site.register(SourceCode)
admin.site.register(ClassName)
admin.site.register(KnowledgePoint2)
admin.site.register(KnowledgePoint1)
admin.site.register(ChoiceProblem)
