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
            "tickets_received",
            "tickets_resolved",
            "first_reply_time_avg",
            "resolution_time_avg",
            "csat",
            "refunds",
            "chargebacks_opened",
            "chargebacks_processed",
            "notes",
            "tag",
            "tag_details",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "first_reply_time_avg": forms.TextInput(attrs={"placeholder": "HH:MM:SS"}),
            "resolution_time_avg": forms.TextInput(attrs={"placeholder": "HH:MM:SS"}),
        }

    def __init__(self, *args, **kwargs):
        clients = kwargs.pop("clients", None)
        super().__init__(*args, **kwargs)
        if clients is not None:
            self.fields["client"].queryset = clients
