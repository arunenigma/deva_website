from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    """Upload files with this form"""
    class Meta:
        model = Document
        exclude = ('md5',)
