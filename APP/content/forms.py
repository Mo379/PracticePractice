from django import forms
from mdeditor.fields import MDTextFormField
from content.models import ExampleModel


class MDEditorModleForm (forms.ModelForm):

    class Meta:
        model = ExampleModel
        fields = '__all__'
