import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get Halo user by searching for Zendesk user ID in 'Other 5' field"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-z", "--zendeskuserid", type=int, help="Zendesk user ID", required=False
        )
        group.add_argument(
            "-e", "--zendeskemail", type=str, help="Zendesk email address", required=False
        )
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Halo credentials",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        if "zendeskuserid" in options:
            search_term = options["zendeskuserid"]
        elif "zendeskemail" in options:
            search_term = options["zendeskemail"]
        else:
            search_term = ""
        user = halo_client.get(f"users?search={search_term}")

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    zendesk_user_id=search_term, timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(user, output_file, indent=4)
        else:
            json.dump(user, self.stdout, indent=4)
