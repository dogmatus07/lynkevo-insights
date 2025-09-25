from django.db import models
import json


class KPIReport(models.Model):
    """
    Enhanced KPI Report model matching the Google Docs reporting format
    """

    PERIOD_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    TAG_CHOICES = [
        ("faulty_items", "Faulty Items"),
        ("delivery_status", "Delivery Status"),
        ("missing_items", "Missing Items"),
        ("return_refund", "Return & Refund"),
        ("infos_requested", "Infos Request"),
        ("claim_out_of_period", "Claim Out of Period"),
    ]

    TAG_DETAILS = {
        "faulty_items": [
            "Ampoule (autonomie, luminosité, télécommande)",
            "Adhésif (faible adhérence)",
            "Produit cassé ou endommagé à la réception",
        ],
        "delivery_status": [
            "Suivi de commande",
            "Produit non reçu",
            "Retard de livraison",
        ],
        "missing_items": [
            "Bulbs qu'ils ont oubliés d'acheter",
            "Articles oubliés par Yakkyo",
        ],
        "return_refund": [
            "Produit-Défectueux / Quality Issues",
            "Produit-Défectueux / Lamps Issue",
            "Produit-Défectueux / Bulbs Related Issues",
            "Produit-Défectueux / Base & Shades",
            "Erreur-Commande",
            "Cancel Requests",
            "Non-Réception",
            "Retour-Refusé",
            "Satisfaction-Subjective",
            "Échange-Remplacement",
            "Retard dans la réponse",
            "Réclamation liée au support",
        ],
        "infos_requested": [
            "Bulbs included or not",
            "Prix-Promotion",
            "Caractéristiques du produit",
            "Délais de livraison",
            "Autres",
        ],
        "claim_out_of_period": [
            "Réclamation hors période",
        ],
    }

    # Basic Information
    client = models.ForeignKey(
        "accounts.Client", on_delete=models.CASCADE, related_name="kpi_reports"
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    shop_name = models.CharField(max_length=200, blank=True, help_text="e.g., Pridola UK")
    slack_channel = models.CharField(max_length=100, blank=True, default="#customer-service-weekly-update")

    # 1. Key Metrics - Response Times
    first_response_time_avg = models.DurationField(null=True, blank=True)
    first_response_sla_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage of inquiries responded to within SLA"
    )
    resolution_time_avg = models.DurationField(null=True, blank=True)
    resolution_48h_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage of tickets resolved within 48 hours"
    )

    # 1. Key Metrics - Ticket Volume
    tickets_received = models.PositiveIntegerField(default=0, help_text="Total support tickets opened")
    tickets_resolved = models.PositiveIntegerField(default=0, help_text="Total inquiries resolved")
    tickets_still_open = models.PositiveIntegerField(default=0, help_text="Total tickets still open")
    tickets_reopened = models.PositiveIntegerField(default=0)
    tickets_unresolved = models.PositiveIntegerField(default=0)

    # 2. Weekly Highlights - Most Common Requests
    # Stored as JSON to allow dynamic addition
    common_requests = models.JSONField(
        default=dict, blank=True,
        help_text="JSON object with request types and counts"
    )
    refund_replacement_requests = models.JSONField(
        default=dict, blank=True,
        help_text="JSON object with refund/replacement types and counts"
    )

    # Refund and Chargeback Management
    total_refund_requests = models.PositiveIntegerField(default=0)
    chargebacks_processed = models.PositiveIntegerField(default=0)
    chargebacks_opened = models.PositiveIntegerField(default=0)

    # 3. Observations and Challenges
    positive_trends = models.JSONField(
        default=list, blank=True,
        help_text="List of positive observations with counts"
    )
    areas_for_improvement = models.JSONField(
        default=list, blank=True,
        help_text="List of areas needing improvement"
    )
    challenges_faced = models.TextField(blank=True)

    # Additional notes
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("client", "period", "period_start", "period_end")
        ordering = ["-period_start"]

    def __str__(self):
        return f"KPI Report for {self.client.name} ({self.period} starting {self.period_start}) -> {self.period_end}"

    def get_ticket_categories_data(self):
        """Return ticket categories breakdown from related TicketCategory objects"""
        return self.ticket_categories.all()

    def get_total_tickets_categorized(self):
        """Calculate total tickets from categories breakdown"""
        return sum([cat.cases_count for cat in self.ticket_categories.all()])


class TicketCategory(models.Model):
    """
    Individual ticket category breakdown for detailed reporting
    """
    report = models.ForeignKey(KPIReport, on_delete=models.CASCADE, related_name='ticket_categories')
    tag = models.CharField(max_length=50, choices=KPIReport.TAG_CHOICES)
    tag_detail = models.CharField(max_length=200)
    cases_count = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['tag', 'tag_detail']

    def __str__(self):
        return f"{self.get_tag_display()} - {self.tag_detail}: {self.cases_count} cases"

    def save(self, *args, **kwargs):
        # Auto-calculate percentage if total tickets available
        if self.report_id:
            total_tickets = self.report.get_total_tickets_categorized()
            if total_tickets > 0:
                self.percentage = (self.cases_count / total_tickets) * 100
        super().save(*args, **kwargs)


class WeeklyHighlight(models.Model):
    """
    Individual weekly highlight entries
    """
    HIGHLIGHT_TYPES = [
        ('common_request', 'Most Common Request'),
        ('positive_trend', 'Positive Trend'),
        ('improvement_area', 'Area for Improvement'),
        ('challenge', 'Challenge Faced'),
        ('observation', 'General Observation'),
    ]

    report = models.ForeignKey(KPIReport, on_delete=models.CASCADE, related_name='highlights')
    highlight_type = models.CharField(max_length=20, choices=HIGHLIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of cases if applicable")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['highlight_type', 'title']

    def __str__(self):
        count_str = f" ({self.count})" if self.count else ""
        return f"{self.get_highlight_type_display()}: {self.title}{count_str}"