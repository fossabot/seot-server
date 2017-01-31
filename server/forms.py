from django import forms
from django.forms import ModelForm
from .models import App


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


# class AppDefineFileForm(ModelForm):
#     class Meta:
#         model = AppDefineFile
#         fields = ['user', 'name', 'yaml_file']
#
#
class AppForm(ModelForm):
    class Meta:
        model = App
        fields = ['name', 'define_file']
