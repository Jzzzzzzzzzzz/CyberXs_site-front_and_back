from django.shortcuts import render,HttpResponse
def index(request):
    return render(request, "index.html")

def trye(request):
    return render(request, "AI.html")

def Privacy_policy(request):
    return HttpResponse("Privacy Policy")
