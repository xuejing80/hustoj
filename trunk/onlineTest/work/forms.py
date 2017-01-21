from django import forms


class TestForm(forms.Form):
    problem_id = forms.IntegerField()
    code = forms.TimeField(widget=forms.Textarea)

