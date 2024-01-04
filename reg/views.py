from django.shortcuts import render,HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
#import
from cyberXsite.models import *



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("save")
            user=form.save()
            print(user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            print(f"save user: {username} {password} ")
            user = authenticate(username=username, password=password)
            django_login(request,user)
            return redirect('/')
    else:
        form = UserCreationForm()
        print("Error")
    return render(request, 'reg.html', {'form': form})

def login(request):
    return HttpResponse("Страница входа")

# Create your views here.
