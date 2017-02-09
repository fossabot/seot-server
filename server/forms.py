from django.forms import ModelForm
from .models import App


class AppForm(ModelForm):
    class Meta:
        model = App
        fields = ['name', 'define_file']
