from django import forms
from django.core import validators
from product_guide.models import File


class UploadFileForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = File
        fields = ['title', 'file']
