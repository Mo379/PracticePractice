from django import forms
from mdeditor.fields import MDTextFormField
from content.models import Point

class MDEditorModleForm(forms.ModelForm):

    class Meta:
        model = Point
        fields = ['p_MDcontent']
        labels = {
                'p_MDcontent': 'Editor',
            }
