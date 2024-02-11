from django.shortcuts import render,HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
#import
from .forms import UserLoginForm,UserRegistationForm





def register(request):
    if request.method == 'POST':
        form = UserRegistationForm(request.POST)
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
        print("hey")
        form = UserRegistationForm()
        print("Error")
    return render(request, 'auth_reg.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect(reverse('index'))

def entry(request):
    redirect_url = reverse('index')
    if request.method=="POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(username=username,password=password)
            print(f"username:{username},password:{password}")
            if user:
                django_login(request,user)
                return redirect(redirect_url)
    else:
        form = UserLoginForm()
    # if request.method == "GET":
    #     if request.user.is_authenticated:
    #         return redirect(redirect_url)
    #     else:
    #         return render(request, 'entry.html')
    # username = request.POST['username']
    # password = request.POST['password']
    # print(username, password)
    # username = str(username)
    # password = str(password)
    # user = authenticate(username=username, password=password)
    # print(password)
    # print(user)
    # if user is not None:
    #     django_login(request, user)
    #     return redirect(redirect_url)
    # print("Error")
    context = {
        "form": form
    }
    return render(request,"entry-login.html",context)

# Create your views here.
