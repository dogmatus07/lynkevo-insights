from django.urls import path
from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.kpi_overview, name="kpi_overview"),
    path("new/", views.kpi_create, name="kpi_create"),
]
