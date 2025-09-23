from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import KPIReportForm
from .models import KPIReport
from accounts.models import Client
from django.contrib.auth.decorators import login_required
import json


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
    Enhanced KPI overview with metrics and filtering.
    """
    clients = user_clients(request.user)
    qs = KPIReport.objects.filter(client__in=clients).select_related("client")
    
    # Filters
    client_slug = request.GET.get("client")
    period_filter = request.GET.get("period")
    active_client = None
    active_client_name = None
    
    if client_slug:
        qs = qs.filter(client__slug=client_slug)
        active_client = client_slug
        # Get the client name for display
        try:
            selected_client = clients.get(slug=client_slug)
            active_client_name = selected_client.name
        except Client.DoesNotExist:
            pass
        
    if period_filter:
        qs = qs.filter(period=period_filter)
    
    # Calculate summary metrics
    summary_metrics = qs.aggregate(
        total_reports=Count('id'),
        total_tickets_received=Sum('tickets_received'),
        total_tickets_resolved=Sum('tickets_resolved'),
        total_refunds=Sum('total_refund_requests'),  # ✅ Corrigé: était 'refunds'
        total_chargebacks=Sum('chargebacks_opened'),
        # ✅ Supprimé avg_csat car le champ n'existe pas dans le modèle
    )
    
    # Add calculated fields to each report
    reports_with_calculations = []
    for report in qs.order_by('-created_at')[:200]:
        # Calculate resolution rate
        resolution_rate = 0
        if report.tickets_received > 0:
            resolution_rate = round((report.tickets_resolved / report.tickets_received) * 100)
        
        # Add calculated field
        report.resolution_rate = resolution_rate
        reports_with_calculations.append(report)
    
    # Get period choices for filter
    period_choices = KPIReport.PERIOD_CHOICES
    
    context = {
        "reports": reports_with_calculations,
        "clients": clients,
        "active_client": active_client,
        "active_client_name": active_client_name,
        "period_filter": period_filter,
        "period_choices": period_choices,
        "summary_metrics": summary_metrics,
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
            messages.success(request, "KPI Report created successfully!")
            return redirect("dashboard:kpi_overview")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = KPIReportForm(clients=clients)
    
    return render(request, "dashboard/kpi_form.html", {"form": form})


@login_required
def dashboard_analytics(request):
    """
    Analytics dashboard with charts and insights.
    """
    clients = user_clients(request.user)
    
    # Date range filter (last 6 months by default)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)
    
    reports = KPIReport.objects.filter(
        client__in=clients,
        period_start__gte=start_date,
        period_end__lte=end_date
    ).select_related('client')
    
    # Data for charts
    monthly_data = {}
    client_performance = {}
    
    for report in reports:
        # Monthly trends
        month_key = report.period_start.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'tickets_received': 0,
                'tickets_resolved': 0,
                'refunds': 0  # ✅ Gardé 'refunds' comme clé pour les données JSON (pas le champ DB)
            }
        
        monthly_data[month_key]['tickets_received'] += report.tickets_received
        monthly_data[month_key]['tickets_resolved'] += report.tickets_resolved
        monthly_data[month_key]['refunds'] += report.total_refund_requests  # ✅ Corrigé: accès au champ DB
        
        # Client performance
        client_name = report.client.name
        if client_name not in client_performance:
            client_performance[client_name] = {
                'total_tickets': 0,
                'total_resolved': 0,
                'total_refunds': 0,
            }
        
        client_performance[client_name]['total_tickets'] += report.tickets_received
        client_performance[client_name]['total_resolved'] += report.tickets_resolved
        client_performance[client_name]['total_refunds'] += report.total_refund_requests  # ✅ Corrigé
    
    # Calculate resolution rates (supprimé CSAT car non disponible)
    for client_data in client_performance.values():
        if client_data['total_tickets'] > 0:
            client_data['resolution_rate'] = (client_data['total_resolved'] / client_data['total_tickets']) * 100
        else:
            client_data['resolution_rate'] = 0
    
    # Top performers by resolution rate (au lieu de CSAT)
    top_resolution_clients = sorted(
        [(name, data['resolution_rate']) for name, data in client_performance.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    context = {
        'monthly_data': json.dumps(monthly_data),
        'client_performance': json.dumps(client_performance),
        'top_resolution_clients': top_resolution_clients,  # ✅ Changé de top_csat_clients
        'date_range': f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}",
        'total_reports': reports.count(),
    }
    
    return render(request, 'dashboard/analytics.html', context)