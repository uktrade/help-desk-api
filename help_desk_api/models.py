from typing import Any

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField

ZENDESK = "zendesk"
HALO = "halo"
HELP_DESK_CHOICES = [
    (ZENDESK, "Zendesk"),
    (HALO, "Halo"),
]


class HelpDeskCreds(models.Model):
    """
    Username and password are Halo username and password
    DRF token should be set to Zendesk token
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # We need to know if this has been updated so we can hash it if it has
        self._zendesk_token = self.zendesk_token

    # If performing object creation without calling save use this to set token
    def set_token(self, raw_token):
        self.zendesk_token = make_password(raw_token)

    is_cleaned = False

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "zendesk_subdomain",
                    "zendesk_email",
                    "zendesk_token",
                ],
                name="zendesk_subdomain_email_token",
            ),
        ]

    halo_client_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    halo_client_secret = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    zendesk_email = models.EmailField()

    zendesk_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # This cannot be ascertained from request (it's defined by
    # where it's not rather than the request details)
    zendesk_subdomain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Needs at least one choice, enforced by not having null=True on the field
    help_desk = MultiSelectField(
        max_length=12,
        max_choices=2,
        choices=HELP_DESK_CHOICES,
        default=ZENDESK,
    )

    last_modified = models.DateTimeField(auto_now=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)

        # self.help_desk.choices:
        if ZENDESK not in self.help_desk:
            raise ValidationError(
                {
                    "help_desk": "You must have Zendesk chosen until go system go live",
                }
            )
        self.is_cleaned = True

    # Enforce the fact that Zendesk MUST be selected until we go live
    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean_fields()

        # Should always have a value so crap out if not
        assert self.zendesk_token

        if self._zendesk_token != self.zendesk_token:
            self.set_token(self.zendesk_token)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.zendesk_email}"
