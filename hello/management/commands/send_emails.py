# yourapp/management/commands/send_emails.py
from django.core.management.base import BaseCommand
from hello.models import EmailConfiguration
from hello.models import db_model
import time
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from smtplib import SMTPException


class Command(BaseCommand):
    help = 'Send emails'

    def handle(self, *args, **kwargs):
        config = EmailConfiguration.objects.first()
        if config.auto_email_sending_active:
            try:
                # Initialize lists to store successful and failed email addresses
                successful_emails = []
                failed_emails = []

                # Retrieve all records where email_sent is False
                records = db_model.objects.filter(email_sent=False)

                batch_size = 20  # Number of emails to send at a time
                batch_delay = 300  # Delay in seconds between batches

                total_records = len(records)
                num_batches = (total_records + batch_size - 1) // batch_size

                for batch_number in range(num_batches):
                    start_index = batch_number * batch_size
                    end_index = min((batch_number + 1) *
                                    batch_size, total_records)
                    batch_records = records[start_index:end_index]

                    for record in batch_records:
                        subject = "Here is your QR code for check-in"
                        recipient_list = [record.email]
                        template = "hello/qr_code/qr_code_email.html"
                        context = {
                            'first_name': record.first_name,
                            'last_name': record.last_name,
                            'id_number': record.id_number,
                            'email': record.email,
                            'table_number': record.table_number,
                        }

                        email_content = render_to_string(template, context)

                        email = EmailMessage(
                            subject, email_content, settings.DEFAULT_FROM_EMAIL, recipient_list)

                        try:
                            email.send()
                            record.email_sent = True
                            record.save()
                            successful_emails.append(record.email)
                        except SMTPException as smtp_error:
                            # Handle SMTP exceptions (e.g., connection issues) here
                            self.stderr.write(self.style.ERROR(
                                f"SMTP Exception for {record.email}: {str(smtp_error)}"))
                            failed_emails.append(record.email)

                    if batch_number < num_batches - 1:
                        time.sleep(batch_delay)

                self.stdout.write(self.style.SUCCESS(
                    'Emails sent successfully.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"An error occurred: {str(e)}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Auto email sending is deactivated.'))
