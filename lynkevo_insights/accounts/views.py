from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Client, Membership
from .forms import ClientForm, MembershipForm, UserCreationForm
import json


def is_staff_or_superuser(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_superuser)
def client_list(request):
    """
    List all clients with search and filtering capabilities
    """
    search_query = request.GET.get('search', '')
    clients_list = Client.objects.annotate(
        reports_count=Count('kpi_reports'),
        users_count=Count('memberships')
    ).order_by('-created_at')
    
    if search_query:
        clients_list = clients_list.filter(
            Q(name__icontains=search_query) |
            Q(contact_email__icontains=search_query)
        )
    
    paginator = Paginator(clients_list, 12)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    
    # Statistics
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(kpi_reports__isnull=False).distinct().count()
    total_reports = sum([client.reports_count for client in clients_list])
    
    context = {
        'clients': clients,
        'search_query': search_query,
        'stats': {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'total_reports': total_reports,
            'inactive_clients': total_clients - active_clients,
        }
    }
    return render(request, 'accounts/client_list.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def client_create(request):
    """
    Create a new client
    """
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client "{client.name}" has been created successfully! 🎉')
            return redirect('accounts:client_detail', pk=client.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm()
    
    return render(request, 'accounts/client_form.html', {
        'form': form,
        'action': 'Create',
        'title': 'Create New Client'
    })


@login_required
@user_passes_test(is_staff_or_superuser)
def client_detail(request, pk):
    """
    Client detail view with KPI reports and user management
    """
    client = get_object_or_404(Client, pk=pk)
    
    # Get recent KPI reports
    recent_reports = client.kpi_reports.order_by('-created_at')[:5]
    
    # Get client memberships
    memberships = client.memberships.select_related('user').order_by('-id')
    
    # Calculate metrics
    total_reports = client.kpi_reports.count()
    total_tickets_received = sum([r.tickets_received for r in client.kpi_reports.all()])
    total_tickets_resolved = sum([r.tickets_resolved for r in client.kpi_reports.all()])
    avg_csat = client.kpi_reports.aggregate(avg_csat=models.Avg('csat'))['avg_csat']
    
    context = {
        'client': client,
        'recent_reports': recent_reports,
        'memberships': memberships,
        'metrics': {
            'total_reports': total_reports,
            'total_tickets_received': total_tickets_received,
            'total_tickets_resolved': total_tickets_resolved,
            'avg_csat': avg_csat,
            'resolution_rate': (total_tickets_resolved / total_tickets_received * 100) if total_tickets_received > 0 else 0,
        }
    }
    return render(request, 'accounts/client_detail.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def client_edit(request, pk):
    """
    Edit client information
    """
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client "{client.name}" has been updated successfully! ✨')
            return redirect('accounts:client_detail', pk=client.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'accounts/client_form.html', {
        'form': form,
        'client': client,
        'action': 'Edit',
        'title': f'Edit {client.name}'
    })


@login_required
@user_passes_test(is_staff_or_superuser)
def client_delete(request, pk):
    """
    Delete client (with confirmation)
    """
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f'Client "{client_name}" has been deleted successfully.')
        return redirect('accounts:client_list')
    
    return render(request, 'accounts/client_confirm_delete.html', {'client': client})


@login_required
@user_passes_test(is_staff_or_superuser)
def add_user_to_client(request, client_pk):
    """
    Add a user to a client with specific role
    """
    client = get_object_or_404(Client, pk=client_pk)
    
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.client = client
            
            # Check if membership already exists
            existing = Membership.objects.filter(
                user=membership.user,
                client=client
            ).first()
            
            if existing:
                existing.role = membership.role
                existing.save()
                messages.success(request, f'Updated {membership.user.username} role to {membership.get_role_display()}')
            else:
                membership.save()
                messages.success(request, f'Added {membership.user.username} as {membership.get_role_display()} to {client.name}')
            
            return redirect('accounts:client_detail', pk=client.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MembershipForm()
    
    return render(request, 'accounts/add_user_to_client.html', {
        'form': form,
        'client': client
    })


@login_required
@user_passes_test(is_staff_or_superuser)
def user_management(request):
    """
    User management dashboard
    """
    search_query = request.GET.get('search', '')
    users_list = User.objects.annotate(
        clients_count=Count('membership__client', distinct=True)
    ).order_by('-date_joined')
    
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    # Statistics
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    context = {
        'users': users,
        'search_query': search_query,
        'stats': {
            'total_users': total_users,
            'staff_users': staff_users,
            'active_users': active_users,
            'regular_users': total_users - staff_users,
        }
    }
    return render(request, 'accounts/user_management.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def create_user(request):
    """
    Create new user account
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been created successfully! 🎉')
            return redirect('accounts:user_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/create_user.html', {'form': form})


@login_required
def dashboard_home(request):
    """
    Main dashboard - different views for staff vs regular users
    """
    if request.user.is_staff or request.user.is_superuser:
        # Staff dashboard with overview
        from dashboard.models import KPIReport
        
        recent_reports = KPIReport.objects.select_related('client').order_by('-created_at')[:5]
        total_clients = Client.objects.count()
        total_reports = KPIReport.objects.count()
        active_clients = Client.objects.filter(kpi_reports__isnull=False).distinct().count()
        
        context = {
            'recent_reports': recent_reports,
            'stats': {
                'total_clients': total_clients,
                'total_reports': total_reports,
                'active_clients': active_clients,
            },
            'is_staff_dashboard': True
        }
    else:
        # Regular user dashboard - redirect to their KPI overview
        return redirect('dashboard:kpi_overview')
    
    return render(request, 'accounts/dashboard_home.html', context)