from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import KPIReport  # ✅ Changé
from accounts.models import Client


@login_required
def report_overview(request):
    """
    View to display the report overview page.
    """
    clients = Client.objects.filter(memberships__user=request.user).distinct()
    qs = KPIReport.objects.filter(client__in=clients).select_related(
        "client"
    )  # ✅ Changé
    client_slug = request.GET.get("client")
    if client_slug:
        qs = qs.filter(client__slug=client_slug)
    context = {
        "reports": qs[:200],
        "clients": clients,
        "active_client": client_slug,
    }
    return render(request, "reports/report_overview.html", context)


@login_required
def generate_report(request):
    """
    View to generate a new report.
    """
    clients = Client.objects.filter(memberships__user=request.user).distinct()
    # Placeholder for report generation logic
    if request.method == "POST":
        client_id = request.POST.get("client")
        if client_id and clients.filter(id=client_id).exists():
            # Logic to generate report for the selected client
            pass
        else:
            # Handle invalid client selection
            pass
    context = {
        "clients": clients,
    }
    return render(request, "reports/generate_report.html", context)
