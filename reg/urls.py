from django.urls import path
from .views import *

urlpatterns = [
    path('reg/', register, name="reg"),
    path('login/', login, name="entry"),
]