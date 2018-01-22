from django.db import models
from auth_system.models import MyUser
from .choices import MAXNUMBER_CHOICES

class ProblemCategory(models.Model):
    """
    程序设计课题目的种类，用语言来区分
    """
    id = models.AutoField(primary_key=True)
    category = models.CharField(verbose_name='题目类别', max_length=30)

    def __str__(self):
        return str(self.category)

class ShejiProblem(models.Model):
    problem_id = models.AutoField('题目id', primary_key=True)
    creator = models.ForeignKey(MyUser, related_name='ShejiProblem_creator')
    title = models.CharField(verbose_name='标题', max_length=200)
    editorText=models.TextField(blank=True, null=True)
    filename = models.CharField(verbose_name='文件名', max_length=200, null=True)
    content_type = models.CharField(verbose_name='文件类型', max_length=200)
    update_date = models.DateTimeField(auto_now=True, verbose_name='最后修改时间', blank=True, null=True)
    in_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(ProblemCategory, verbose_name='题目类别')
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['problem_id']
        verbose_name = '程序设计题'
        verbose_name_plural = '程序设计题'
    #题目创建者，创建时间，最后修改时间，题目主要功能，题目基本需求，题目描述文件(文件的存储路径[可以为空])

class CodeWeekClass(models.Model):
    """
    程序设计课班级
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='程序设计课班级名称')
    teacher = models.ForeignKey(MyUser, related_name='CodeWeekClass_teacher')
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(ShejiProblem, related_name='CodeWeekClass_problems')
    students = models.ManyToManyField(
        MyUser,
        through='CodeWeekClassStudent',
        through_fields=('codeWeekClass', 'student'),
    )
    numberEachGroup = models.IntegerField(choices=MAXNUMBER_CHOICES, default=1)
    counter = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

STUDENT_STATE = (
    (1, ("初始，需要分组")),
    (2, ("加入分组")),
    (3, ("成为组长")),
    (4, ("可以选题")),
    (5, ("可以提交"))
)

class CodeWeekClassGroup(models.Model):
    """
    用来描述课程中的分组关系
    """
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    cwclass = models.ForeignKey(CodeWeekClass, related_name='CodeWeekClass_group')
    selectedProblem = models.ForeignKey(ShejiProblem, related_name='GroupSelectProblem', on_delete=models.PROTECT, null=True)
    counter = models.IntegerField(default=0)

class CodeWeekClassStudent(models.Model):
    """
    用来描述课程和学生之间的多对多关系
    """
    codeWeekClass = models.ForeignKey(CodeWeekClass)
    student = models.ForeignKey(MyUser)
    state = models.IntegerField(choices=STUDENT_STATE, default=1)
    group = models.ForeignKey(CodeWeekClassGroup, related_name='Group_member', null=True, on_delete=models.SET_NULL)
    isLeader = models.BooleanField(default=False)

    def get_full_name(self):
        return self.student.id_num + " " + self.student.username

class ClassOperation(models.Model):
    """
    记录下每次学生提交成功的操作，对应于每个课有个编号用来标识操作的先后
    """
    id = models.AutoField(primary_key=True)
    cwclass = models.ForeignKey(CodeWeekClass, related_name='Class_operations', null=True, on_delete=models.SET_NULL)
    operation_id = models.IntegerField()
    operation = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)