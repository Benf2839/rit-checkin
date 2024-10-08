from django.utils.timezone import datetime
from django.views.generic import ListView
from django.db import connections
from django.core.paginator import Paginator
from django.urls import reverse
from hello.models import db_model, EmailConfiguration
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
import csv
from django.contrib import messages
from hello.models import db_model
from django.http import FileResponse
import os
import shutil
from io import StringIO
import traceback
import sys
from django.http import HttpResponseServerError
import openpyxl
from django.conf import settings
from django.core.mail import get_connection, EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db import transaction
import time
from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.views.decorators.cache import never_cache
import logging


# Define the regular expression patterns
# Only alphabetic characters, spaces, and dashes
name_pattern = r"^[A-Za-z -]+$"
# Valid email pattern
email_pattern = r"^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def handle_errors_and_redirect(request, errors, redirect_page):
    if errors:
        error_message = ", ".join(errors)
        traceback_str = traceback.format_exc()  # Get the traceback as a string
        # Get the line number of the error
        line_number = traceback.extract_tb(sys.exc_info()[2])[-1][1]
        error_info = f"Error occurred at line {line_number}"
        error_info += f"\nTraceback:\n{traceback_str}"
        messages.error(request, f"{error_message}\n\n{error_info}")
        return render(request, redirect_page, {"errors": errors})


def load_add_new_data_page(request):
    return render(request, "hello/database_upload_page.html")


def redirect_w_backup(request):
    backup_file_path = "/home/guardia2/Web_app/Exports/db_backup.csv"
    if os.path.exists(backup_file_path):
        try:
            return FileResponse(
                open(backup_file_path, "rb"),
                as_attachment=True,
                filename="server_backup.csv",
            )
        except Exception as e:
            error_message = f"Error occurred while processing the backup: {str(e)}"
            return HttpResponseServerError(error_message)
    else:
        messages.error(request, "No Backup found.")  # Display an error message
        # Display an error message
        return HttpResponse(status=200, content="No Backup found.")


def export_master_list(request):
    master_list = db_model.objects.all()
    # Prepare CSV data
    csv_data = []
    csv_data.append(
        [
            "Company_name",
            "First_name",
            "Last_name",
            "Email",
            "Alumni",
            "Release_info",
            "Checked_in",
            "Checked_in_time",
            "Table_number",
            "id_number",
        ]
    )

    for entry in master_list:
        csv_data.append(
            [
                entry.company_name,
                entry.first_name,
                entry.last_name,
                entry.email,
                entry.alumni,
                entry.release_info,
                entry.checked_in,
                entry.checked_in_time,
                entry.table_number,
                entry.id_number,
            ]
        )

    # Create a temporary file to store the CSV data
    temp_csv_file = "Exports/temp.csv"

    with open(temp_csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Define the server backup file name
    server_backup_file = "Exports/server_backup.csv"

    # Check if the server backup file already exists
    if os.path.exists(server_backup_file):
        # Remove the existing server backup file
        # IMPORTANT: WILL NOT WORK IF THE FILE IS OPEN IN A VIEWER WINDOW
        os.remove(server_backup_file)

    # Move the temporary file to the server backup file
    shutil.move(temp_csv_file, server_backup_file)

    # Create a FileResponse to return the file to the browser
    response = FileResponse(open(server_backup_file, "rb"), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="server_backup.csv"'

    # Set the appropriate headers to prompt the file download
    response["Content-Length"] = os.path.getsize(server_backup_file)
    response["Content-Encoding"] = "utf-8"

    # Wipe the Master_list table
    db_model.objects.all().delete()
    messages.success(request, "Master_list table wiped successfully.")

    # Return the CSV file to the browser as download
    response = FileResponse(
        server_backup_file, as_attachment=True, filename="db_backup.csv"
    )
    return response


@login_required
@transaction.atomic
def add_new_data(request, response=None):
    print(request.POST)
    if request.method == "POST":
        print(request.POST)
        if (
            "export" in request.POST
        ):  # Export the current entries in the Master_list table
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="master_list.csv"'
            writer = csv.writer(response)
            # Retrieve data from the database (assuming you're using Django ORM)
            master_list = db_model.objects.all()
            # Write the header row
            writer.writerow(
                [
                    "Company_name",
                    "First_name",
                    "Last_name",
                    "Email",
                    "Alumni",
                    "Release_info",
                    "Checked_in",
                    "Checked_in_time",
                    "Table_number",
                    "id_number",
                ]
            )
            # Write data rows
            for entry in master_list:
                writer.writerow(
                    [
                        entry.company_name,
                        entry.first_name,
                        entry.last_name,
                        entry.email,
                        entry.alumni,
                        entry.release_info,
                        entry.checked_in,
                        entry.checked_in_time,
                        entry.table_number,
                        entry.id_number,
                    ]
                )  # Replace with actual column values
            # Display a success message
            messages.success(request, "Data exported successfully.")
            return response  # Return the CSV file to the browser as download

        elif "import" in request.POST:  # Import the user selected CSV file
            # Save all current entries in db to the existing_data variable
            existing_data = db_model.objects.all()
            # Get the uploaded file
            try:
                import_from_file = request.FILES["file"]
                messages.success(request, "file is valid")
            except:
                messages.error(request, "Please select a  file for upload.")

            # Process the uploaded file
            try:
                textbox_values = [
                    request.POST.get("Company_Name_box"),
                    request.POST.get("First_Name_box"),
                    request.POST.get("Last_Name_box"),
                    request.POST.get("Email_box"),
                    request.POST.get("Alumni_box"),
                    request.POST.get("Info_Release_box"),
                    request.POST.get("Table_Number_box"),
                ]
                messages.success(request, "Variables are: " + str(textbox_values))
                # Convert box numbers from letters to numbers
                box_mapping = {
                    "a": 0,
                    "b": 1,
                    "c": 2,
                    "d": 3,
                    "e": 4,
                    "f": 5,
                    "g": 6,
                    "h": 7,
                    "i": 8,
                    "j": 9,
                    "k": 10,
                    "l": 11,
                    "m": 12,
                    "n": 13,
                    "o": 14,
                    "p": 15,
                }

                # Map textbox values to column indices
                column_indices = [
                    box_mapping[value.lower()] if value else None
                    for value in textbox_values
                ]

                # Process the uploaded file
                uploaded_file = request.FILES.get("file")
                file_extension = uploaded_file.name.split(".")[-1]

                if file_extension == "csv":
                    csv_data = uploaded_file.read().decode(
                        "utf-8"
                    )  # Read the file as text
                    csv_file = StringIO(csv_data)
                    reader = csv.reader(csv_file)
                    next(reader)  # Skip the header row
                elif file_extension == "xlsx":
                    wb = openpyxl.load_workbook(uploaded_file)
                    ws = wb.active
                    reader = ws.iter_rows(values_only=True)
                    next(reader)  # Skip the header row
                else:
                    messages.error(request, "Unsupported file format.")
                    return render(request, "hello/database_upload_page.html")

                # Extract the data from each row
                for row in reader:
                    ext_company_name = row[column_indices[0]]
                    ext_first_name_last_name = row[column_indices[1]]

                    # Check if column_indices[1] and column_indices[2] have the same value
                    if column_indices[1] == column_indices[2]:
                        # If they have the same value, split the value at the first space
                        space_index = ext_first_name_last_name.find(" ")
                        if space_index != -1:  # If space exists
                            ext_first_name = ext_first_name_last_name[:space_index]
                            ext_last_name = ext_first_name_last_name[
                                space_index + 1 :
                            ].strip(", ")
                        else:
                            ext_first_name = ext_first_name_last_name
                            ext_last_name = ""
                    else:
                        ext_first_name = ext_first_name_last_name
                        ext_last_name = row[column_indices[2]]

                    ext_email = row[column_indices[3]]
                    ext_alumni = row[column_indices[4]]
                    ext_release_info = row[column_indices[5]]
                    ext_table_number = row[column_indices[6]]

                    # Rest of your code remains unchanged...

                    # Check if all required fields are empty
                    if (
                        ext_company_name
                        or ext_first_name
                        or ext_last_name
                        or ext_email
                        or ext_alumni
                        or ext_release_info
                    ):

                        # Perform validations on the data
                        errors = []
                        # If there are any errors, render the current page with the error messages
                        if errors:
                            error_message = ", ".join(errors)
                            traceback_str = (
                                traceback.format_exc()
                            )  # Get the traceback as a string
                            line_number = None

                            tb = traceback.extract_tb(sys.exc_info()[2])
                            if tb:
                                # Get the line number of the error
                                line_number = tb[-1][1]

                            error_info = (
                                f"Error occurred at line {line_number}"
                                if line_number
                                else "Error information not available"
                            )
                            error_info += f"\nTraceback:\n{traceback_str}"
                            messages.error(request, f"{error_message}\n\n{error_info}")
                            return render(
                                request,
                                "hello/database_upload_page.html",
                                {"errors": errors},
                            )
                        else:
                            # Map "yes" and "no" values to boolean values
                            boolean_map = {
                                "yes": True,
                                "Yes": True,
                                "no": False,
                                "No": False,
                            }

                            # Convert "yes" and "no" values to boolean values
                            # If the value is not "yes" or "no", set it to None
                            ext_alumni = boolean_map.get(ext_alumni, None)
                            # If the value is not "yes" or "no", set it to None
                            ext_release_info = boolean_map.get(ext_release_info, None)

                            # Create a new entry in the Master_list table
                            entry = db_model(
                                # assign the id_number column with the Django auto-incremented value
                                id_number=None,
                                company_name=ext_company_name,
                                first_name=ext_first_name,
                                last_name=ext_last_name,
                                email=ext_email,
                                alumni=ext_alumni,
                                release_info=ext_release_info,
                                checked_in=False,
                                checked_in_time=None,
                                table_number=ext_table_number,
                                email_sent=False,
                            )
                            entry.save()  # Save the entry to the database

                messages.success(request, "Data imported successfully.")
                # Render the database upload page
                return render(request, "hello/database_upload_page.html")

            except Exception as e:  # Handle any other exceptions
                error_message = f"Error processing the CSV file: {str(e)}"
                traceback_str = traceback.format_exc()  # Get the traceback as a string
                # Display the exception and traceback as an error message
                messages.error(
                    request, f"{error_message}\n\nTraceback:\n{traceback_str}"
                )
                # Redirect to the database upload page
                return redirect(add_new_data)
        # else:
        # return render(request, 'hello/database_upload_page.html') # Render the database upload page
    else:
        # If the request is not a POST request, render the database upload page
        # Render the database upload page
        return render(request, "hello/database_upload_page.html")


def export_data(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="master_list.csv"'
    writer = csv.writer(response)
    # Retrieve data from the database
    master_list = db_model.objects.all()
    # Write the header row
    writer.writerow(
        [
            "Company_name",
            "First_name",
            "Last_name",
            "Email",
            "Alumni",
            "Release_info",
            "Checked_in",
            "Checked_in_time",
            "Table_number",
            "id_number",
        ]
    )
    # Write data rows
    for entry in master_list:
        writer.writerow(
            [
                entry.company_name,
                entry.first_name,
                entry.last_name,
                entry.email,
                entry.alumni,
                entry.release_info,
                entry.checked_in,
                entry.checked_in_time,
                entry.table_number,
                entry.id_number,
            ]
        )  # Replace with actual column values
    # Display a success message
    messages.success(request, "Data exported successfully.")
    return response  # Return the CSV file to the browser as download


def send_reset_email(request):
    if request.method == "POST":
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        ) as connection:
            subject = request.POST.get("Password Reset")
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [
                request.POST.get("email"),
            ]
            message = request.POST.get("message")
            EmailMessage(
                subject, message, email_from, recipient_list, connection=connection
            ).send()

    return render(request, "password_reset_email.html")


@never_cache
def email_sending_status(request):
    try:
        # Retrieve the EmailConfiguration instance (assuming it has an ID of 1)
        config, created = EmailConfiguration.objects.get_or_create(
            id=1, defaults={"auto_email_sending_active": False}
        )

        if request.method == "POST":
            # Check if the user submitted the form to change the email sending status
            new_status = request.POST.get("email_sending_status")
            if new_status in ["on", "off"]:
                config.auto_email_sending_active = new_status == "on"
                config.save()
                messages.success(request, "Email sending status updated successfully.")

        # Get the value of the auto_email_sending_active column (already boolean)
        currentStatus = config.auto_email_sending_active

        return render(
            request,
            "hello/qr_code/send_qr_code.html",
            {"currentStatus": currentStatus, "config": config},
        )

    except EmailConfiguration.DoesNotExist:
        # Handle the case where no EmailConfiguration instance with ID 1 is found
        # Create a new EmailConfiguration instance with auto_email_sending_active set to False
        config = EmailConfiguration(id=1, auto_email_sending_active=False)
        config.save()
        return redirect(
            "email_sending_status"
        )  # Redirect to the same view to display the form


def email_configuration_page(request):
    # Retrieve the EmailConfiguration instance (assuming it has an ID of 1)
    try:
        config = EmailConfiguration.objects.get(pk=1)
    except EmailConfiguration.DoesNotExist:
        # Handle the case where the EmailConfiguration with ID 1 does not exist
        config = None

    return render(request, "hello/qr_code/send_qr_code.html", {"config": config})


"""
def send_qr_emails(request):
    if request.method == "POST":
        try:
            # Initialize lists to store successful and failed email addresses
            successful_emails = []
            failed_emails = []

            # Retrieve all records where email_sent is False
            records = db_model.objects.filter(email_sent=False)

            batch_size = getattr(settings, 'BATCH_SIZE', 20)  # Get BATCH_SIZE from settings, default to 50 if not set
            batch_delay = getattr(settings, 'BATCH_DELAY', 300)  # Get BATCH_DELAY from settings, default to 300 seconds if not set

            total_records = len(records)
            num_batches = (total_records + batch_size - 1) // batch_size

            for batch_number in range(num_batches):
                start_index = batch_number * batch_size
                end_index = min((batch_number + 1) * batch_size, total_records)
                batch_records = records[start_index:end_index]

                for record in batch_records:
                    subject = "Here is your QR code for check-in"
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

                    # Create an EmailMessage object and send it
                    email = EmailMessage(
                        subject, email_content, settings.DEFAULT_FROM_EMAIL, recipient_list)

                    try:
                        email.send()
                        # Change email_sent to True for the current record
                        record.email_sent = True
                        record.save()
                        successful_emails.append(record.email)
                    except Exception as e:
                        failed_emails.append(record.email)

                # Add a cooldown period between batches
                if batch_number < num_batches - 1:
                    time.sleep(batch_delay)

            # Display success message with the number of emails queued
            messages.success(
                request, f"{len(successful_emails)} emails queued successfully.")

            # Display error message with the list of failed email addresses
            if failed_emails:
                messages.error(
                    request, f"Failed to queue emails for the following addresses: {', '.join(failed_emails)}")

        except Exception as e:
            messages.error(
                request, f"An error occurred while queuing emails: {str(e)}")

    return render(request, 'hello/qr_code/qr_code_email_sent.html')
"""


def qr_email_page(request):
    return render(request, "hello/qr_code/send_qr_code.html")


def qr_email_success(request):
    return render(request, "hello/qr_code/qr_code_email_sent.html")


class HomeListView(ListView):
    """Renders the home page, with a list of all logs."""

    model = db_model

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context


def about(request):
    """Renders the about page."""
    return render(request, "hello/about.html")


def contact(request):
    """Renders the contact page."""
    return render(request, "hello/contact.html")


def on_site_entry_success(request):
    table_number = request.GET.get("table_number")
    context = {"table_number": table_number}
    return render(request, "hello/on_site_entry_success.html", context)


@login_required
@transaction.atomic
def search_by_id(request):  # searches the database for a specific id number
    try:
        # gets the id number from the search bar
        id_number = request.GET.get("Id_number")
        if id_number:  # if the id number exists
            # first() returns the first object matched by the queryset
            checkin = db_model.objects.filter(id_number=id_number).first()
        else:  # if the id number does not exist
            checkin = False  # set checkin to false
        # context is a dictionary that maps variable names to objects
        context = {"Checkin": checkin}
        # renders the id search results page
        return render(request, "hello/id_search_results.html", context)
    except Exception as e:  # if an error occurs
        # display an error message
        messages.error(
            request,
            f"The following error occurred while searching for the ID number: {str(e)}",
        )
        return render(request, "hello/search.html")  # renders the search page


# @login_required
@transaction.atomic
def add_entry(request):
    if request.method == "POST":
        # Retrieve form data
        company_name = request.POST.get("company_name")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        alumni = bool(request.POST.get("alumni"))
        release_info = bool(request.POST.get("release_info"))
        # id_number = request.POST.get('id_number')
        # table_number = request.POST.get('table_number')

        # Perform form validation
        errors = 0

        # if not company_name.isalpha():
        #   messages.error(request, f'Please enter a valid company name')
        #    errors = 1

        if not first_name.isalpha():
            messages.error(request, f"Please enter a valid first name")
            errors = 1

        if not last_name.isalpha():
            messages.error(request, f"Please enter a valid last name")
            errors = 1

        if not email:
            messages.error(request, f"Please enter a valid email address")
            errors = 1

        # If there are errors, render the form with error messages
        if errors > 0:
            return render(request, "hello/add_entry.html")

        current_time = datetime.now()
        time_to_subtract = timedelta(hours=4)
        shifted_datetime = current_time - time_to_subtract

        # Create an instance of db_model model and set the field values
        checkin_entry = db_model(
            company_name=company_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            alumni=alumni,
            release_info=release_info,
            # id_number=int(id_number),
            checked_in=True,
            checked_in_time=shifted_datetime,  # Autopopulate with current time and date,
            # table_number=table_number,
            email_sent=False,
        )

        # Save the instance to the database
        checkin_entry.save()

        return redirect("/on_site_entry_success")  # Redirect to a success page

    return render(request, "hello/add_entry.html")


def self_registration(request):
    if request.method == "POST":
        try:
            # Retrieve form data
            company_name = request.POST.get("company_name")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            alumni = bool(request.POST.get("alumni"))
            release_info = bool(request.POST.get("release_info"))

            # Perform form validation
            errors = {}

            if not company_name.isalpha():
                messages.error(request, f"please enter a valid company name")

            if not first_name.isalpha():
                messages.error(request, f"please enter a valid first name")

            if not last_name.isalpha():
                messages.error(request, f"please enter a valid last name")

            if not email:
                messages.error(request, f"please enter a valid email address")

            # If there are errors, render the form with error messages
            # if errors:
            #    return render(request, 'hello/self_registration_page.html', {'errors': errors})
        except Exception as e:
            messages.error(
                request, f"An error occurred while sending the email: {str(e)}"
            )

        # Create an instance of db_model model and set the field values
        checkin_entry = db_model(
            company_name=company_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            alumni=alumni,
            release_info=release_info,
            checked_in=False,
            # checked_in_time=timezone.now(),  # model already sets time every time a change is made
            email_sent=True,
        )

        # Save the instance to the database
        checkin_entry.save()
        messages.success(request, f"Succesfully registered")

        try:
            # Get the email from the POST data
            input_email = request.POST.get("email")
            messages.success(request, "email address " + input_email)
            # Retrieve the corresponding record from the database based on the ID number
            record = get_object_or_404(db_model, email=input_email)

            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
            ) as connection:
                subject = "Here is your QR code for check-in"
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [record.email]
                template = (
                    "hello/qr_code/qr_code_email.html"  # Path to the email template
                )
                context = {
                    "first_name": record.first_name,
                    "last_name": record.last_name,
                    "email": record.email,
                    "table_number": record.table_number,
                    "id_number": record.id_number,
                }  # Add any additional context variables if needed

                # Render the email content using the template and context
                email_content = render_to_string(template, context)
                messages.success(request, "email content has been created")
                # Send the email
                EmailMessage(
                    subject,
                    email_content,
                    email_from,
                    recipient_list,
                    connection=connection,
                ).send()
                # Change email_sent to True for matching record
                record = get_object_or_404(db_model, email=input_email)
                record.email_sent = True
                record.save()

        except Exception as e:
            messages.error(
                request, f"An error occurred while sending the email: {str(e)}"
            )

        return redirect("/self_reg_success")  # Redirect to a success page

    return render(request, "hello/self_registration_page.html")


def self_reg_success(request):
    return render(request, "hello/self_reg_success.html")


def QR_entry_success(request):
    return render(request, "hello/QR_entry_success.html")


@login_required
@transaction.atomic
def update_entry(request):
    if request.method == "POST":
        # Retrieve form data
        id_number = request.POST.get("id_number")

        # Retrieve the existing entry with the matching ID
        try:
            checkin_entry = db_model.objects.get(id_number=int(id_number))
        except db_model.DoesNotExist:
            # Handle the case when the entry does not exist
            context = {"error1": True, "id_number": id_number}
            return render(request, "hello/search.html", context)

        # Check if the user is already checked in
        if checkin_entry.checked_in:
            context = {"error2": True, "id_number": id_number}
            return render(request, "hello/search.html", context)

        # Update the field values of the existing entry
        checkin_entry.company_name = request.POST.get("company_name")
        checkin_entry.first_name = request.POST.get("first_name")
        checkin_entry.last_name = request.POST.get("last_name")
        checkin_entry.email = request.POST.get("email")
        checkin_entry.alumni = bool(request.POST.get("alumni"))
        checkin_entry.release_info = bool(request.POST.get("release_info"))
        checkin_entry.checked_in = True
        checkin_entry.checked_in_time = timezone.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # Autopopulate with current time and date

        # Save the updated entry to the database
        checkin_entry.save()
        context = {
            "company_name": checkin_entry.company_name,
            "table_number": checkin_entry.table_number,
        }
        # Redirect to the 'QR_entry_success' view with the context data
        return render(request, "hello/QR_entry_success.html", context)


@login_required
def db_display(request, page=1):
    # Check if filter_blanks parameter is present in the URL
    filter_blanks = request.GET.get("filter_blanks")

    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT * FROM Master_list")
        rows = cursor.fetchall()

    converted_rows = []
    for row in rows:
        converted_row = list(row)
        # Convert 'alumni' field
        if converted_row[5] == 1:
            converted_row[5] = "yes"
        elif converted_row[5] == 0:
            converted_row[5] = "no"
        else:
            converted_row[5] = "null"  # Handle null value
        # Convert 'release_info' field
        if converted_row[6] == 1:
            converted_row[6] = "yes"
        elif converted_row[6] == 0:
            converted_row[6] = "no"
        else:
            converted_row[6] = "null"  # Handle null value
        # Convert 'checked_in' field
        if converted_row[7] == 1:
            converted_row[7] = "yes"
        elif converted_row[7] == 0:
            converted_row[7] = "no"
        else:
            converted_row[7] = "null"  # Handle null value
        # Convert 'email_sent' field
        if converted_row[10] == 1:
            converted_row[10] = "yes"
        elif converted_row[10] == 0:
            converted_row[10] = "no"
        else:
            converted_row[10] = "null"
        converted_rows.append(converted_row)

    # Filter rows with empty entries if 'filter_blanks' is in the request
    if filter_blanks == "true":
        # Filter rows with blanks
        filtered_rows = [row for row in converted_rows if "null" in row]
    else:
        # Show all entries
        filtered_rows = converted_rows

    # the number sets the number of records per page
    paginator = Paginator(filtered_rows, 25)
    page_obj = paginator.get_page(page)

    return render(request, "hello/db_display.html", {"page_obj": page_obj})


@login_required
@transaction.atomic
def search_by_id(request):
    context = {}
    if "id_number" in request.GET:
        messages.info(request, "You searched for: {}".format(request.GET["id_number"]))
        id_number = request.GET["id_number"]
        try:
            entry = db_model.objects.get(id_number=id_number)
            context["entry"] = entry
            messages.success(request, "Entry found.")
        except db_model.DoesNotExist:
            messages.error(request, "There is no corresponding entry for that number.")
            return render(request, "hello/search.html", context)

    return render(request, "hello/search.html", context)


def homepage(request):
    return render(request, "hello/home.html")


# below is the code for the apple wallet pass


# def generate_pass_view(request, serial_number):
#    pass_instance = get_object_or_404(Pass, serial_number=serial_number)
#
#    pass_data = {
#        "serialNumber": pass_instance.serial_number,
#        # Add more pass data fields as needed
#    }
#
#    pass_path = pass_instance.generate_pass(pass_data)
#
#    with open(pass_path, "rb") as f:
#        response = HttpResponse(f.read(), content_type="application/vnd.apple.pkpass")
#        response["Content-Disposition"] = f'attachment; filename="{pass_data["serialNumber"]}.pkpass"'
#
#    return response
