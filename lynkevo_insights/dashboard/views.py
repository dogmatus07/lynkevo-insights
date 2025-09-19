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
def kpi_overview(request):
    """
    View to display the KPI overview page.
    """
    clients = user_clients(request.user)
    qs = KPIReport.objects.filter(client__in=clients).select_related("client")
    client_slug = request.GET.get("client")
    active_client = None

    if client_slug:
        qs = qs.filter(client__slug=client_slug)
        active_client = client_slug
    context = {
        "reports": qs[:200],
        "clients": clients,
        "active_client": active_client,
    }
    return render(request, "dashboard/kpi_overview.html", context)


@login_required
def kpi_create(request):
    """
    View to create a new KPI report.
    """
    clients = user_clients(request.user)
    if request.method == "POST":
        form = KPIReportForm(request.POST, clients=clients)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI Report created successfully.")
            return redirect("dashboard:kpi_overview")
    else:
        form = KPIReportForm(clients=clients)
    return render(request, "dashboard/kpi_form.html", {"form": form})
