from django import forms

from hello.models import LogMessage
from hello.models import db_model

class EntryForm(forms.ModelForm):
    class Meta:
        model = db_model
        fields = '__all__'

