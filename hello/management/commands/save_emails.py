from django.core.management.base import BaseCommand
from hello.functions import save_emails_as_text  # Import your function


class Command(BaseCommand):
    # ... (unchanged code)

    def handle(self, *args, **kwargs):
        batch_size = 20  # Set your desired batch size here
        status, successful_emails, failed_emails = save_emails_as_text(batch_size)

        # Print status messages
        self.stdout.write(self.style.SUCCESS(f"Status: {status}"))
        self.stdout.write(self.style.SUCCESS(f"Successful emails: {successful_emails}"))

        # Print detailed error data for failed emails
        for failed_email in failed_emails:
            if isinstance(failed_email, dict):
                if "email" in failed_email:
                    self.stdout.write(
                        self.style.ERROR(f'Failed email: {failed_email["email"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR("Failed email: Unknown recipient")
                    )
                if "error" in failed_email:
                    self.stdout.write(
                        self.style.ERROR(f'Error details: {failed_email["error"]}')
                    )
            else:
                # Handle entries in failed_emails that are not dictionaries
                self.stdout.write(
                    self.style.ERROR(
                        f"Unexpected format for failed email: {failed_email}"
                    )
                )
