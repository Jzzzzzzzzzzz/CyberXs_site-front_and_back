from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from cyberXsite.models import MyModel
from django.contrib.auth.models import User


class UserLoginForm(AuthenticationForm):
    # username = forms.CharField()
    # password = forms.CharField()
    username = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={"autofocus": True,
                                                             "class": "form-control",
                                                             "placeholder": "name@example.com", }))
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          "class": "form-control",
                                          "placeholder": "pas", })
    )
    class Meta:
        model=User
        fields = ["username","password"]
class UserRegistationForm(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()
    class Meta:
     model = User
     fields = (
         "username","password1","password2"
     )






