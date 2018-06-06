from django import forms
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from mooc.models import Resource,Week,Type
from judge.models import ClassName

class ResourceAddForm(forms.Form):
    num = forms.CharField(label='资源序号', widget=forms.Textarea(
        attrs={'class': 'form-control', 'required': 'required','rows': '1'}))
    title = forms.CharField(label='资源标题', widget=forms.Textarea(
        attrs={'class': 'form-control', 'required': 'required','rows': '1'}))
    link = forms.CharField(label='资源链接',max_length=200, widget=forms.Textarea(
        attrs={'class': 'form-control', 'required': 'required', 'rows': '3'}))
    type = forms.ModelChoiceField(label='资源类型', queryset=Type.objects.all(),
                                       widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    courser = forms.ModelChoiceField(label='所属课程', queryset=ClassName.objects.all(),
                                       widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    week = forms.ModelChoiceField(label='所属周次', queryset=Week.objects.all(),
                                       widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    def save(self, user, id=None):
        cd = self.cleaned_data
        if id:
            with transaction.atomic():
                resource= Resource.objects.select_for_update().get(pk=id)
                resource.num = cd['num']
                resource.title = cd['title']
                resource.type = cd['type']
                resource.link = cd['link']
                resource.courser = cd['courser']
                resource.week = cd['week']
                resource.creater=user
                resource.save()
        else:
            resource = Resource(creater=user,num=cd['num'],title=cd['title'], type=cd['type'], courser=cd['courser'], week=cd['week'],link=cd['link'])
            resource.save()
        resource.save()
        return resource