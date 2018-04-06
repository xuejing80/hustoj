from django import forms
from .models import ShejiProblem, ProblemCategory
from .choices import MAXNUMBER_CHOICES

class AddCodeWeekForm(forms.Form):
    course_name = forms.CharField(label='coursename', max_length=100, required=True)
    begin_time = forms.DateTimeField(label='begintime', required=True)
    end_time = forms.DateTimeField(label='endtime', required=True)
    problems = forms.CharField(required=False)
    maxnumber = forms.ChoiceField(choices=MAXNUMBER_CHOICES, required=True)

class ShejiAddForm(forms.Form):
    title = forms.CharField(label='标题', widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-validation': 'required', 'data-validation-error-msg': "请输入题目标题"}))
    editorText = forms.CharField(label='题目描述',widget=forms.Textarea(
        attrs={'class': 'form-control', 'required':  'required', 'rows': '10'}))
    headImg = forms.FileField(label='描述文件', widget=forms.FileInput(
        attrs={'data-validation': 'required', 'data-validation-error-msg': "请上传文件"}))
    category = forms.ModelChoiceField(label='题目类别', queryset=ProblemCategory.objects.all(),
                                       widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    def save(self, user):
        cd = self.cleaned_data
        title = cd['title']
        editorText=cd['editorText']
        headImg=cd['headImg']
        category=cd['category']
        problem =ShejiProblem(
            creator=user,
            title=title,
            editorText=editorText,
            filename=headImg.name,
            content_type=headImg.content_type,
            category=category
        )
        problem.save()
        return problem

class ShejiUpdateForm(forms.Form):
    title = forms.CharField(label='标题', widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-validation': 'required', 'data-validation-error-msg': "请输入题目标题"}))
    editorText = forms.CharField(label='题目描述',widget=forms.Textarea(
        attrs={'class': 'form-control', 'required':  'required', 'rows': '10'}))
    headImg = forms.FileField(label='更新文件', required=False)
    category = forms.ModelChoiceField(label='题目类别', queryset=ProblemCategory.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    def save(self, user, problemid):
        cd = self.cleaned_data
        title = cd['title']
        editorText=cd['editorText']
        headImg=cd['headImg']
        category=cd['category']
        problem = ShejiProblem.objects.get(pk=problemid)
        problem.title = title
        problem.editorText=editorText
        if headImg:
            problem.filename=headImg.name
            problem.content_type = headImg.content_type
        if category:
            problem.category = category
        problem.save()
        return problem

class UpdateClassForm(forms.Form):
    problems = forms.CharField(required=False)
    students = forms.Textarea()

class SubmitCodeForm(forms.Form):
    codeFile = forms.FileField(required=True)
    contribution = forms.CharField(required=True)

class UploadReportForm(forms.Form):
    report = forms.FileField(required=True)