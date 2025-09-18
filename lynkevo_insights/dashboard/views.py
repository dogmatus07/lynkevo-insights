from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import KPIReportForm
from .models import KPIReport
from accounts.models import Client
from django.contrib.auth.decorators import login_required


def user_clients(user):
    """
    Returns a queryset of clients associated with the given user.
    """
    if user.is_staff or user.is_superuser:
        return Client.objects.all()
    return Client.objects.filter(memberships__user=user).distinct()


@login_required
def create_kpi_report(request):
    """
    View to create a new KPI report.
    """
    clients = user_clients(request.user)

    qs = KPIReport.objects.filter(client__in=clients).select_related('client')
    client_slug = request.GET.get('client')
    if client_slug:
        )



