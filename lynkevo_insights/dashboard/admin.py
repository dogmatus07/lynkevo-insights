from django.contrib import admin
from .models import KPIReport, TicketCategory, WeeklyHighlight


@admin.register(KPIReport)
class KPIReportAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "period",
        "period_start",
        "period_end",
        "shop_name",
        "tickets_received",
        "tickets_reopened",
        "tickets_resolved",
        "tickets_unresolved",
        "tickets_still_open",
        "first_response_time_avg",  # ✅ Corrigé: était "first_reply_time_avg"
        "resolution_time_avg",
        "total_refund_requests",  # ✅ Corrigé: était "refunds"
        "chargebacks_opened",
        "chargebacks_processed",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "client",
        "period",
        "period_start",
        "period_end",
        # ✅ Supprimé "tag" car il n'existe pas dans KPIReport
    )
    
    search_fields = ("client__name", "shop_name")
    ordering = ("-created_at",)
    
    # Champs en lecture seule (calculés automatiquement)
    readonly_fields = ("created_at", "updated_at")
    
    # Groupement des champs dans l'interface admin
    fieldsets = (
        ("Basic Information", {
            "fields": ("client", "period", "period_start", "period_end", "shop_name", "slack_channel")
        }),
        ("Response Times", {
            "fields": ("first_response_time_avg", "first_response_sla_percentage", 
                      "resolution_time_avg", "resolution_48h_percentage")
        }),
        ("Ticket Volume", {
            "fields": ("tickets_received", "tickets_resolved", "tickets_still_open", 
                      "tickets_reopened", "tickets_unresolved")
        }),
        ("Financial Metrics", {
            "fields": ("total_refund_requests", "chargebacks_opened", "chargebacks_processed")
        }),
        ("Observations", {
            "fields": ("notes", "challenges_faced", "common_requests", "refund_replacement_requests",
                      "positive_trends", "areas_for_improvement"),
            "classes": ("collapse",)  # Section repliable
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "tag",
        "tag_detail",
        "cases_count",
        "percentage",
    )
    
    list_filter = (
        "tag",
        "report__client",
        "report__period",
    )
    
    search_fields = ("tag_detail", "report__client__name")
    ordering = ("report", "tag", "tag_detail")


@admin.register(WeeklyHighlight)
class WeeklyHighlightAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "highlight_type",
        "title",
        "count",
        "created_at",
    )
    
    list_filter = (
        "highlight_type",
        "report__client",
        "report__period",
    )
    
    search_fields = ("title", "description", "report__client__name")
    ordering = ("report", "highlight_type", "title")