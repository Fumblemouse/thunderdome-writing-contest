"""Describes custom forms"""
from django import forms
from .models import Story


class BaseForm(forms.ModelForm):
    """BaseForm bootstrapping:
        this provides bootstrap classes to all fields of particular types"""
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if "Boolean" not in str(field):
                field.widget.attrs['class'] = 'form-control'
            #else:
            #    field.widget.attrs['class'] = 'form-check-input'

class StoryForm(BaseForm):
    """USer enters Story and Title"""

    class Meta:
        model = Story
        fields = ('title', 'content','access')
