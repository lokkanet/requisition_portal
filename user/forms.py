from random import choices
from select import select
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *
from django.core.exceptions import ValidationError
from .widget import DatePickerInput

from django.forms import ModelForm, Select

class RequisitionForm(ModelForm):
    class Meta:
        model = Requisition
        fields = '__all__'
        widgets = {
            'date_of_delivery' : DatePickerInput(),
            
            
        }

    send_to = forms.ModelMultipleChoiceField(
        queryset=NewUser.objects.all(),
        widget=forms.SelectMultiple,
        
    )
    
class UpdateForm(ModelForm):
    class Meta:
        model = Requisition
        fields = ['date_of_delivery', 'status']
        widgets = {
            'date_of_delivery' : DatePickerInput(),
            
            
        }

    


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)


    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username','first_name', 'last_name', 'email','password1', 'password2']:
            self.fields[fieldname].help_text = None
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        

    allowed_domain = ['bdren.net.bd']

    def clean_email(self):
        email_doamin = self.cleaned_data['email'].split('@')[-1]
       

        if email_doamin not in self.allowed_domain:
            raise forms.ValidationError("Please supply an email address provided by BdREN.")
        
        return self.cleaned_data['email']




