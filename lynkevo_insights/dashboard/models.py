from django.db import models


class KPIReport(models.Model):
    """
    Model to store Key Performance Indicator (KPI) reports for clients.

    Each report includes metrics such as ticket counts, response times, customer satisfaction (CSAT),
    refunds, and chargebacks over a specified period (weekly or monthly).

    Attributes:
        client (ForeignKey): Reference to the client for whom the report is generated.
        period (CharField): The reporting period, either 'weekly' or 'monthly'.
        period_start (DateField): The start date of the reporting period.

        period_end (DateField): The end date of the reporting period.
        tickets_created (PositiveIntegerField): Number of tickets created during the period.
        tickets_resolved (PositiveIntegerField): Number of tickets resolved during the period.
        first_reply_time_avg (DurationField): Average time taken for the first reply to tickets.
        resolution_time_avg (DurationField): Average time taken to resolve tickets.
        csat (DecimalField): Customer satisfaction score as a percentage.
        refunds (PositiveIntegerField): Number of refunds issued during the period.
        chargebacks_opened (PositiveIntegerField): Number of chargebacks opened during the period.
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

    client = models.ForeignKey(
        "accounts.Client", on_delete=models.CASCADE, related_name="kpi_reports"
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()

    # About ticket status
    tickets_received = models.PositiveIntegerField(default=0)
    tickets_reopened = models.PositiveIntegerField(default=0)
    tickets_resolved = models.PositiveIntegerField(default=0)
    tickets_unresolved = models.PositiveIntegerField(default=0)
    tickets_still_open = models.PositiveIntegerField(default=0)

    # About ticket time metrics
    first_reply_time_avg = models.DurationField(null=True, blank=True)
    resolution_time_avg = models.DurationField(null=True, blank=True)

    # About customer satisfaction and financial metrics
    csat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    refunds = models.PositiveIntegerField(default=0)
    chargebacks_opened = models.PositiveIntegerField(default=0)
    chargebacks_processed = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tag related fields
    tag = models.CharField(max_length=50, choices=TAG_CHOICES, null=True, blank=True)
    tag_details = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ("client", "period", "period_start", "period_end")
        ordering = ["-period_start"]

    def __str__(self):
        return f"KPI Report for {self.client.name} ({self.period} starting {self.period_start}) -> {self.period_end}"
