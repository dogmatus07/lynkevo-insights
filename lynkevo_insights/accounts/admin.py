from django.contrib import admin
from .models import Client, Membership


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface for the Client model.
    """

    list_display = ("name", "contact_email", "created_at", "updated_at", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """
    Admin interface for the Membership model.
    """

    list_display = ("user", "client", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "client__name")
