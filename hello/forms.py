from django import forms

from hello.models import LogMessage
from hello.models import db_model
from .models import EmailConfiguration  # Import the EmailConfiguration model

class EntryForm(forms.ModelForm):
    class Meta:
        model = db_model
        fields = '__all__'



class EmailConfigurationForm(forms.ModelForm):
    class Meta:
        model = EmailConfiguration
        fields = ['auto_email_sending_active']
