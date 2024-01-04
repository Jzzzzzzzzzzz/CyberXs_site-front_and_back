from django.db import models
from django.contrib import admin
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse


User = get_user_model()
class MyModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
# Create your models here.
