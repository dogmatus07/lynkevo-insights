from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_overview, name="report_overview"),
    path("generate/", views.generate_report, name="generate_report"),
]
