from django import forms
from .models import KPIReport


class KPIReportForm(forms.ModelForm):
    """
    A form for creating and updating KPI reports.
    """

    class Meta:
        model = KPIReport
        fields = [
            "client",
            "period",
            "period_start",
            "period_end",
            "shop_name",
            "slack_channel",
            # Response Times
            "first_response_time_avg",  # ✅ Corrigé: était "first_reply_time_avg"
            "first_response_sla_percentage",
            "resolution_time_avg",
            "resolution_48h_percentage",
            # Ticket Volume
            "tickets_received",
            "tickets_resolved",
            "tickets_still_open",
            "tickets_reopened",
            "tickets_unresolved",
            # Refunds and Chargebacks
            "total_refund_requests",  # ✅ Corrigé: était "refunds"
            "chargebacks_opened",
            "chargebacks_processed",
            # Notes
            "notes",
            "challenges_faced",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "challenges_faced": forms.Textarea(attrs={"rows": 3}),
            "slack_channel": forms.TextInput(attrs={"placeholder": "#customer-service-weekly-update"}),
            "shop_name": forms.TextInput(attrs={"placeholder": "e.g., Pridola UK"}),
            "first_response_time_avg": forms.TextInput(attrs={"placeholder": "HH:MM:SS"}),
            "resolution_time_avg": forms.TextInput(attrs={"placeholder": "HH:MM:SS"}),
        }

    def __init__(self, *args, **kwargs):
        clients = kwargs.pop("clients", None)  # ✅ Corrigé
        super().__init__(*args, **kwargs)
        if clients is not None:
            self.fields["client"].queryset = clients  # ✅ Corrigé


class TicketCategoryForm(forms.ModelForm):
    """
    Form for creating ticket categories breakdown
    """
    class Meta:
        model = KPIReport  # Cette relation se fait via TicketCategory
        fields = []  # Les tags sont gérés via le modèle TicketCategory séparément