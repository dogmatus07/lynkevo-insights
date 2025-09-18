from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Client(models.Model):
    """Model representing a client. Each client is associated with a user."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Generate a slug for the client based on the name.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Membership(models.Model):
    """
    Model representing a membership plan for clients.
    """

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="viewer")

    class Meta:
        unique_together = ("user", "client")

    def __str__(self):
        return f"{self.user.username} - {self.client.name} ({self.role})"
