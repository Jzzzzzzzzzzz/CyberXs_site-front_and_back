from django.urls import path
from .views import *

urlpatterns = [
    path('reg/', register, name="reg"),
    path('entry/', entry, name="entry"),
    path('logout/', logout_view, name="logout")
]