from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from hello.models import db_model, EmailConfiguration  # Import your models

def send_emails_in_batches(batch_size):
    try:
        # Check if auto email sending is enabled
        email_config = EmailConfiguration.objects.filter(pk=1).first()
        if email_config and email_config.auto_email_sending_active == 0:
            return [], ["Auto email sending is disabled, so no emails were sent."]

        # Initialize lists to store successful and failed email addresses
        successful_emails = []
        failed_emails = []

        # Retrieve all records where email_sent is False and limit to batch_size
        records = db_model.objects.filter(email_sent=False)[:batch_size]

        for record in records:
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
            except Exception as e:
                # Append the failed email and exception details to the failed_emails list
                failed_emails.append({'email': record.email, 'error': str(e)})

        return successful_emails, failed_emails

    except Exception as e:
        return [], [{'error': str(e)}]
