

from mailqueue.models import MailerMessage
from django.conf import settings
from hello.models import db_model
from django.template.loader import render_to_string
import django
import os

# Set the Django settings module.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hello.production_settings")

# Initialize Django
django.setup()


# Now you can import other Django modules


def send_qr_emails():
    try:
        # Initialize lists to store successful and failed email addresses
        successful_emails = []
        failed_emails = []

        # Retrieve all records where email_sent is False
        records = db_model.objects.filter(email_sent=False)

        for record in records:
            subject = "Here is your QR code for check-in"
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [record.email]
            template = "hello/qr_code/qr_code_email.html"  # Path to the email template
            context = {
                'first_name': record.first_name,
                'last_name': record.last_name,
                'id_number': record.id_number,
                'email': record.email,
                'table_number': record.table_number,
            }  # Add any additional context variables if needed

            # Render the email content using the template and context
            email_content = render_to_string(template, context)

            # Create a MailerMessage object and save it to the mail queue
            msg = MailerMessage()
            msg.subject = subject
            msg.to_address = record.email
            msg.from_address = f'{settings.DEFAULT_FROM_EMAIL} <{settings.EMAIL_HOST_USER}>'
            msg.html_content = email_content

            try:
                # Save the email to the mail queue
                msg.save()
                # Change email_sent to True for the current record
                record.email_sent = True
                record.save()
                successful_emails.append(record.email)
            except Exception as e:
                failed_emails.append(record.email)

        # Log or handle any exceptions here if needed

    except Exception as e:
        # Log or handle any exceptions here if needed
        pass
