from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,ValidationError
from cyberXsite.models import MyModel
from django.contrib.auth.models import User


class UserLoginForm(AuthenticationForm):
    # username = forms.CharField()
    # password = forms.CharField()
    username = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={"autofocus": True,
                                      "class": "inp",
                                      "placeholder": "name@example.com", }))
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          "class": "inp",
                                          "placeholder": "pas", })
    )
    class Meta:
        model=User
        fields = ["username","password"]
#  {{form.username}} {{form.username.id_for_label}}
class UserRegistationForm(UserCreationForm):

    username = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={"autofocus": True,
                                      "class": "inp",
                                      "placeholder": "name@example.com",
                                      }))
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          "class": "inp",
                                          "placeholder": "password",}))
    password2 = forms.CharField(
         label="Повторите пароль",
         widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                           "class": "inp",
                                           "placeholder": "password2"}))
    class Meta:
        model = User
        fields = (
            "username", "password1","password2"
        )







