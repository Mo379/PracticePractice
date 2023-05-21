from django import forms
from mdeditor.fields import MDTextFormField
from content.models import Point, Question

class MDEditorModleForm(forms.ModelForm):

    class Meta:
        model = Point
        fields = ['p_MDcontent']
        labels = {
                'p_MDcontent': 'Editor',
            }


class MDEditorQuestionModleForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['q_MDcontent']
        labels = {
                'q_MDcontent': 'Editor',
            }


class MDEditorAnswerModleForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['q_MDcontent_ans']
        labels = {
                'q_MDcontent_ans': 'Editor',
            }
