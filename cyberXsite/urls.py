from django.urls import path

from .views import *

urlpatterns = [
    path('', index,name="index"),
    path("try/",trye,name="try"),
    path("Privacy-Policy/",Privacy_policy,name="Privacy_policy"),
    path('soc/', soc, name="soc"),
    path('analyse/', ai_handler, name='engagement_analysis'),
]
