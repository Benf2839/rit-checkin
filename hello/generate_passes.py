# Create a script or management command (e.g., generate_passes.py) in your app's management/commands directory.

from django.core.management.base import BaseCommand
from hello.models import Pass, db_model
from django_walletpass.models import PassBuilder

class Command(BaseCommand):
    help = 'Generate passes for existing entries in db_model'

    def handle(self, *args, **options):
        primary_entries = db_model.objects.all()
        for entry in primary_entries:
            pass_instance, created = Pass.objects.get_or_create(primary_entry=entry)


builder=PassBuilder(directory='passes\Event.pass\pass.json')

builder.pass_data.update({
    "barcode": {
        "message":"123456789",
        "format":"PKBarcodeFormatPDF417",
        "messageEncoding":"iso-8859-1"
    },
    "organizationName":"RIT Career Services",
    "description":"RIT Career Fair Ticket",
})

pass_instance = builder.write_to_model(Pass)
pass_instance.save()