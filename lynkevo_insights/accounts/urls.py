from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    
    # Dashboard home
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    
    # Client Management (Staff only)
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),
    path("clients/<int:client_pk>/add-user/", views.add_user_to_client, name="add_user_to_client"),
    
    # User Management (Staff only)
    path("users/", views.user_management, name="user_management"),
    path("users/create/", views.create_user, name="create_user"),
]