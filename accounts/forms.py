from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django_countries.fields import CountryField  # type: ignore

class SingUpForm(UserCreationForm):
    country = CountryField().formfield()
    class Meta:
        model = User
        fields =('username','country','password1','password2')
        exclude = ['usable_password']
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['Country']