# tasks.py in your app
from celery import shared_task
from django.conf import settings
from hello.celery_config import app
from celery.utils.log import get_task_logger
from django.template.loader import render_to_string
from mailqueue.models import MailerMessage  # Import MailerMessage
from .models import db_model

logger = get_task_logger(__name__)


@shared_task(rate_limit='10/m')  # Add rate limiting if needed
def send_qr_code_email(record_id):
    try:
        # Retrieve the record by ID
        record = db_model.objects.get(id=record_id)

        subject = "Here is your QR code for check-in"
        # Use Django's settings for email_from
        email_from = settings.DEFAULT_FROM_EMAIL

        # Construct the recipient list as a list of recipient emails
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

        # Create a MailerMessage instance and save it to the mail queue
        msg = MailerMessage()
        msg.subject = subject
        msg.from_address = email_from
        msg.to_address = ', '.join(recipient_list)  # Join recipient emails
        msg.content = email_content
        msg.save()

        # Change email_sent to True for the current record
        record.email_sent = True
        record.save()

        logger.info(f"Email queued successfully for {record.email}")
    except Exception as e:
        logger.error(f"Email queueing failed: {str(e)}")
