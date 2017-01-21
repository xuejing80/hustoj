from django.db import models

from auth_system.models import MyUser

# Create your models here.
from work.models import HomeworkAnswer, MyHomework


class ClassName(models.Model):
    name = models.CharField(verbose_name='课程名称', max_length=30)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'class_name'
        verbose_name = '课程名称'
        verbose_name_plural = '课程名称'


class KnowledgePoint1(models.Model):
    name = models.CharField(verbose_name='一级知识点名称', max_length=20)
    id = models.AutoField(primary_key=True)
    classname = models.ForeignKey(ClassName, verbose_name='所属课程')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'knowledge_point_1'
        verbose_name = '一级知识点'
        verbose_name_plural = '一级知识点'


class KnowledgePoint2(models.Model):
    name = models.CharField(verbose_name='二级知识点名称', max_length=20)
    upperPoint = models.ForeignKey(KnowledgePoint1, verbose_name='上级课程')
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'knowledge_point_2'
        verbose_name = '二级知识点'
        verbose_name_plural = '二级知识点'


class ChoiceProblem(models.Model):
    id = models.AutoField('选择题ID', primary_key=True)
    title = models.TextField(max_length=200)
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)
    c = models.CharField(max_length=50)
    d = models.CharField(max_length=50)
    right_answer = models.CharField(max_length=1)
    creater = models.ForeignKey(MyUser)
    update_date = models.DateTimeField(auto_now=True, verbose_name='最后修改时间', blank=True, null=True)
    in_date = models.DateTimeField(auto_now_add=True)
    knowledgePoint1 = models.ManyToManyField(KnowledgePoint1, verbose_name='一级知识点')
    knowledgePoint2 = models.ManyToManyField(KnowledgePoint2, verbose_name='二级知识点')
    classname = models.ManyToManyField(ClassName, verbose_name='所属课程')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']
        verbose_name = '选择题'
        verbose_name_plural = '选择题'


class Problem(models.Model):
    problem_id = models.AutoField('题目id', primary_key=True)
    title = models.CharField(verbose_name='标题', max_length=200)
    description = models.TextField('描述', blank=True, null=True)
    input = models.TextField('输入描述', blank=True, null=True)
    output = models.TextField('输出描述', blank=True, null=True)
    sample_input = models.TextField('样例输入1', blank=True, null=True)
    sample_output = models.TextField('样例输出1', blank=True, null=True)
    sample_input2 = models.TextField('样例输入2', blank=True, null=True)
    sample_output2 = models.TextField('样例输出2', blank=True, null=True)
    spj = models.CharField(max_length=1, default=0)
    hint = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    in_date = models.DateTimeField('录入时间', blank=True, null=True, auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, verbose_name='最后修改时间', blank=True, null=True)
    time_limit = models.IntegerField('限制时间', default=1)
    memory_limit = models.IntegerField('限制内存', default=128)
    defunct = models.CharField(max_length=1, default='N')
    accepted = models.IntegerField('AC数量', blank=True, null=True, default=0)
    submit = models.IntegerField('提交数量', blank=True, null=True, default=0)
    solved = models.IntegerField(blank=True, null=True)
    knowledgePoint1 = models.ManyToManyField(KnowledgePoint1, verbose_name='一级知识点')
    knowledgePoint2 = models.ManyToManyField(KnowledgePoint2, verbose_name='二级知识点')
    classname = models.ManyToManyField(ClassName, verbose_name='所属课程')
    creater = models.ForeignKey(MyUser)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'problem'
        ordering = ['problem_id']
        verbose_name = '编程题'
        verbose_name_plural = '编程题'


class Runtimeinfo(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'runtimeinfo'


class Solution(models.Model):
    solution_id = models.AutoField(primary_key=True)
    problem_id = models.IntegerField()
    user_id = models.CharField(max_length=48)
    time = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    in_date = models.DateTimeField(auto_now_add=True)
    result = models.SmallIntegerField(default=0)
    language = models.IntegerField(default=0)
    ip = models.CharField(max_length=15)
    contest_id = models.IntegerField(blank=True, null=True)
    valid = models.IntegerField(default=1)
    num = models.IntegerField(default=-1)
    code_length = models.IntegerField(default=0)
    judgetime = models.DateTimeField(blank=True, null=True)
    pass_rate = models.DecimalField(max_digits=2, decimal_places=2, default=0.00)
    lint_error = models.IntegerField(default=0)
    homework_answer = models.ForeignKey(HomeworkAnswer, null=True)
    oi_info = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'solution'

    def __str__(self):
        try:
            return str(self.homework_answer.id)
        except:
            return 'none'


class SourceCode(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    source = models.TextField()

    class Meta:
        db_table = 'source_code'

    def __str__(self):
        return str(self.solution_id)


class SourceCodeUser(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    source = models.TextField()

    class Meta:
        db_table = 'source_code_user'


class Compileinfo(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'compileinfo'
