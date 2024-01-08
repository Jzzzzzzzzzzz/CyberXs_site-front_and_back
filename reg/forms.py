from django import forms
from django.contrib.auth.forms import AuthenticationForm
from cyberXsite.models import MyModel

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True,
                                                             "class": "form-control",
                                                             "placeholder": "name@example.com", }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          "class": "form-control",
                                          "placeholder": "pas", })
    )
    class Meta:
        model=MyModel
        fields = ["username","password"]


