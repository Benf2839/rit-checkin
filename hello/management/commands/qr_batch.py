from django.core.management.base import BaseCommand
from hello.functions import send_emails_in_batches  # Import your function

class Command(BaseCommand):
    help = 'qr_batch'

    def handle(self, *args, **kwargs):
        batch_size = 20  # Set your desired batch size here
        successful_emails, failed_emails = send_emails_in_batches(batch_size)

        # Log or print the results if needed
        self.stdout.write(self.style.SUCCESS(f'Successful emails: {successful_emails}'))

        # Print detailed error data for failed emails
        for failed_email in failed_emails:
            self.stdout.write(self.style.ERROR(f'Failed email: {failed_email["email"]}'))
            self.stdout.write(self.style.ERROR(f'Error details: {failed_email["error"]}'))
