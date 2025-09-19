from django.contrib import admin
from .models import KPIReport


@admin.register(KPIReport)
class KPIReportAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "period",
        "period_start",
        "period_end",
        "tickets_received",
        "tickets_reopened",
        "tickets_resolved",
        "tickets_unresolved",
        "tickets_still_open",
        "first_reply_time_avg",
        "resolution_time_avg",
        "csat",
        "refunds",
        "chargebacks_opened",
        "chargebacks_processed",
        "notes",
        "created_at",
        "updated_at",
        "tag",
        "tag_details",
    )

    list_filter = (
        "client",
        "period",
        "period_start",
        "period_end",
        "tag",
    )
    search_fields = "client__name"
    ordering = ("-created_at",)
