from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from hello.models import db_model  # Replace with your actual model

def send_emails_in_batches(batch_size):
    try:
        # Initialize lists to store successful and failed email addresses
        successful_emails = []
        failed_emails = []

        # Check if auto email sending is active
        config = EmailConfiguration.objects.filter(id=1).first()
        if not config or not config.auto_email_sending_active:
            return successful_emails, ["Auto email sending is disabled, no emails were sent."]

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
                failed_emails.append(f"Email: {record.email}, Error: {str(e)}")

        return successful_emails, failed_emails

    except Exception as e:
        return [], [str(e)]
