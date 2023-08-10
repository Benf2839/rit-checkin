from django.shortcuts import redirect, render
from django.utils.timezone import datetime
from django.views.generic import ListView
from django.db import connections
from django.core.paginator import Paginator
from django.urls import reverse
from hello.models import db_model
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
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
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
import qrcode
from django.http import HttpResponse
from .models import Pass
import datetime

# Define the regular expression patterns
name_pattern = r'^[A-Za-z -]+$'  # Only alphabetic characters, spaces, and dashes
email_pattern = r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'  # Valid email pattern


def handle_errors_and_redirect(request, errors, redirect_page):
    if errors:
        error_message = ', '.join(errors)
        traceback_str = traceback.format_exc()  # Get the traceback as a string
        line_number = traceback.extract_tb(sys.exc_info()[2])[-1][1]  # Get the line number of the error
        error_info = f"Error occurred at line {line_number}"
        error_info += f"\nTraceback:\n{traceback_str}"
        messages.error(request, f"{error_message}\n\n{error_info}")
        return render(request, redirect_page, {'errors': errors})



def load_add_new_data_page(request):
    return render(request, 'hello/database_upload_page.html')

def redirect_w_backup(request):
    backup_file_path = 'https://guardiansforge.net/Web_app/Exports/db_backup.csv' 
    try:
        if os.path.exists(backup_file_path):
            return FileResponse(open(backup_file_path, 'rb'), as_attachment=True, filename='server_backup.csv')
        else:
            return render(request, 'hello/success.html')
    except Exception as e:
        error_message = f'Error occurred while processing the backup: {str(e)}'
        return HttpResponseServerError(error_message)
    

def export_master_list(request):
    master_list = db_model.objects.all()
    # Prepare CSV data
    csv_data = []
    csv_data.append(['Company_name', 'First_name', 'Last_name', 'Email', 'Alumni', 'Release_info', 'Checked_in', 'Checked_in_time', 'Table_number', 'id_number'])

    for entry in master_list:
        csv_data.append([
            entry.company_name, entry.first_name, entry.last_name, entry.email, entry.alumni, entry.release_info, entry.checked_in,
            entry.checked_in_time, entry.table_number, entry.id_number
        ])

    # Create a temporary file to store the CSV data
    temp_csv_file = 'Exports/temp.csv'

    with open(temp_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Define the server backup file name
    server_backup_file = 'Exports/server_backup.csv'

    # Check if the server backup file already exists
    if os.path.exists(server_backup_file):
        # Remove the existing server backup file
        os.remove(server_backup_file) #############IMPORTANT: WILL NOT WORK IF THE FILE IS OPEN IN A VIEWER WINDOW

    # Move the temporary file to the server backup file
    shutil.move(temp_csv_file, server_backup_file)

    # Create a FileResponse to return the file to the browser
    response = FileResponse(open(server_backup_file, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="server_backup.csv"'

    # Set the appropriate headers to prompt the file download
    response['Content-Length'] = os.path.getsize(server_backup_file)
    response['Content-Encoding'] = 'utf-8'

    # Wipe the Master_list table
    db_model.objects.all().delete()
    messages.success(request, 'Master_list table wiped successfully.')

    # Return the CSV file to the browser as download
    response = FileResponse(server_backup_file, as_attachment=True, filename='db_backup.csv')
    return (response)


@login_required
@transaction.atomic
def add_new_data(request, response=None):
    print(request.POST)
    if request.method == 'POST':
        print(request.POST)
        if 'export' in request.POST: # Export the current entries in the Master_list table
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="master_list.csv"'
            writer = csv.writer(response)
            # Retrieve data from the database (assuming you're using Django ORM)
            master_list = db_model.objects.all()
            # Write the header row
            writer.writerow(['Company_name', 'First_name', 'Last_name', 'Email', 'Alumni', 'Release_info', 'Checked_in', 'Checked_in_time', 'Table_number', 'id_number'])  
            # Write data rows
            for entry in master_list:
                writer.writerow([entry.company_name, entry.first_name, entry.last_name, entry.email, entry.alumni, entry.release_info, entry.checked_in, entry.checked_in_time, entry.table_number, entry.id_number])  # Replace with actual column values
            messages.success(request, 'Data exported successfully.') # Display a success message
            return (response) # Return the CSV file to the browser as download
        

        elif 'import' in request.POST: # Import the user selected CSV file
            # Get the uploaded file
                try: 
                    import_from_file = request.FILES['file']
                    messages.success(request, 'file is valid')
                except:
                    messages.error(request, 'Please select a .csv file for upload.')
            
                response = export_master_list(request) # Export the current entries in the Master_list table

                # Process the uploaded CSV file
                try:
                    textbox_values = [
                        request.POST.get('Company_Name_box'),
                        request.POST.get('First_Name_box'),
                        request.POST.get('Last_Name_box'),
                        request.POST.get('Email_box'),
                        request.POST.get('Alumni_box'),
                        request.POST.get('Info_Release_box'),
                        request.POST.get('Table_Number_box'),
                    ]
                    messages.success(request, 'Variables are: ' + str(textbox_values))
                    # Convert box numbers from letters to numbers
                    box_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15}

                    # Map textbox values to column indices
                    column_indices = [box_mapping[value.lower()] if value else None for value in textbox_values]

                    # Process the uploaded file
                    csv_data = import_from_file.read().decode('utf-8')  # Read the file as text

                    # Create a StringIO object to simulate a file-like object
                    csv_file = StringIO(csv_data)

                    # Read the CSV data
                    reader = csv.reader(csv_file)

                    next(reader)  # Skip the header row

                    # Extract the data from each row
                    for row in reader:
                        ext_company_name = row[column_indices[0]]
                        ext_first_name = row[column_indices[1]]
                        ext_last_name = row[column_indices[2]]
                        ext_email = row[column_indices[3]]
                        ext_alumni = row[column_indices[4]]
                        ext_release_info = row[column_indices[5]]
                        ext_table_number = row[column_indices[6]]

                        # Check if all required fields are empty
                        if ext_company_name or ext_first_name or ext_last_name or ext_email or ext_alumni or ext_release_info:
                            
                            # Perform validations on the data
                            errors = []
                            '''if ext_company_name and not re.match(name_pattern, ext_company_name):
                                errors.append('Company name should only contain alphabetic characters, spaces, and dashes.')
                            if ext_first_name and not re.match(name_pattern, ext_first_name):
                                errors.append('First name should only contain alphabetic characters, spaces, and dashes.')
                            if ext_last_name and not re.match(name_pattern, ext_last_name):
                                errors.append('Last name should only contain alphabetic characters, spaces, and dashes.')
                            if not ext_email or not re.match(email_pattern, ext_email):
                                errors.append('Incorrect format for email field')
                            if not ext_alumni:
                                errors.append('Incorrect format for alumni field')
                            if not ext_release_info:
                                errors.append('Incorrect format for release info')'''

                            # If there are any errors, render the current page with the error messages
                            if errors:
                                error_message = ', '.join(errors)
                                traceback_str = traceback.format_exc()  # Get the traceback as a string
                                line_number = None
                                
                                tb = traceback.extract_tb(sys.exc_info()[2])
                                if tb:
                                    line_number = tb[-1][1]  # Get the line number of the error
                                
                                error_info = f"Error occurred at line {line_number}" if line_number else "Error information not available"
                                error_info += f"\nTraceback:\n{traceback_str}"
                                messages.error(request, f"{error_message}\n\n{error_info}")
                                return render(request, 'hello/database_upload_page.html', {'errors': errors})
                            else:
                                # Map "yes" and "no" values to boolean values
                                boolean_map = {
                                    "yes": True,
                                    "no": False
                                }

                                # Convert "yes" and "no" values to boolean values
                                ext_alumni = boolean_map.get(ext_alumni.lower(), False)
                                ext_release_info = boolean_map.get(ext_release_info.lower(), False)

                                # Create a new entry in the Master_list table
                                entry = db_model(
                                    #assign the id_number column with the django autoincremented value
                                    id_number = None,
                                    company_name=ext_company_name,
                                    first_name=ext_first_name,
                                    last_name=ext_last_name,
                                    email=ext_email,
                                    alumni=ext_alumni,
                                    release_info=ext_release_info,
                                    checked_in=False,
                                    checked_in_time=datetime.datetime.now(),
                                    table_number=ext_table_number,
                                    email_sent=False,
                                )
                                entry.save() # Save the entry to the database  
                        else:
                            messages.success(request, 'all columns imported successfully')
                            break  # Stop iterating over rows if all required fields are empty

                    messages.success(request, 'Data imported successfully.')
                    return render(request, 'hello/database_upload_page.html') # Render the database upload page
                
                except Exception as e: # Handle any other exceptions
                    error_message = f'Error processing the CSV file: {str(e)}'
                    traceback_str = traceback.format_exc()  # Get the traceback as a string
                    messages.error(request, f'{error_message}\n\nTraceback:\n{traceback_str}') # Display the exception and traceback as an error message
                    return redirect(add_new_data) # Redirect to the database upload page
    else:
        ## If the request is not a POST request, render the database upload page
        return render(request, 'hello/database_upload_page.html') # Render the database upload page

 

 
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="master_list.csv"'
    writer = csv.writer(response)
    # Retrieve data from the database 
    master_list = db_model.objects.all()
    # Write the header row
    writer.writerow(['Company_name', 'First_name', 'Last_name', 'Email', 'Alumni', 'Release_info', 'Checked_in', 'Checked_in_time', 'Table_number', 'id_number'])  
    # Write data rows
    for entry in master_list:
        writer.writerow([entry.company_name, entry.first_name, entry.last_name, entry.email, entry.alumni, entry.release_info, entry.checked_in, entry.checked_in_time, entry.table_number, entry.id_number])  # Replace with actual column values
    messages.success(request, 'Data exported successfully.') # Display a success message
    return (response) # Return the CSV file to the browser as download



def send_reset_email(request):  
    if request.method == "POST": 
        with get_connection(  
           host=settings.EMAIL_HOST, 
        port=settings.EMAIL_PORT,  
        username=settings.EMAIL_HOST_USER, 
        password=settings.EMAIL_HOST_PASSWORD, 
        use_tls=settings.EMAIL_USE_TLS  
        ) as connection:  
           subject = request.POST.get("Password Reset")  
           email_from = settings.EMAIL_HOST_USER  
           recipient_list = [request.POST.get("email"), ]  
           message = request.POST.get("message")  
           EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()  
 
    return render(request, 'password_reset_email.html')


def send_qr_email(request):
    if request.method == "POST":
        try:
            # Get the ID number from the POST data
            id_number = request.POST.get("id_number")
            messages.success(request, 'id number is ' + id_number)
            # Retrieve the corresponding record from the database based on the ID number
            record = get_object_or_404(db_model, id_number=id_number)
            # Check if email has already been sent to the user
            if record.email_sent:
                return render(request, 'hello/qr_code/qr_code_email.html', {'message': 'Email has already been sent to this user'}) 
            else:
                messages.success(request, 'email has not already been sent')
                with get_connection(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=settings.EMAIL_USE_TLS
                ) as connection:
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
                    messages.success(request, 'email content has been created')
                    # Send the email
                    EmailMessage(subject, email_content, email_from, recipient_list, connection=connection).send()
                    # Change email_sent to True for matching record
                    record.email_sent = True
                    record.save()
        
        except Exception as e:
            messages.error(request, f"An error occurred while sending the email: {str(e)}")

    return render(request, 'hello/qr_code/qr_code_email.html')



def qr_email_page(request):
    return render(request, 'hello/qr_code/send_qr_code.html')

def qr_email_success(request):
    return render(request, 'hello/qr_code/qr_code_email_sent.html')


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


def success(request):
    table_number = request.GET.get('table_number')
    context = {'table_number': table_number}
    return render(request, 'hello/success.html', context)




def hello_there(request, name):
    """Renders the hello_there page.
    Args:
        name: Name to say hello to
    """
    return render(
        request, "hello/hello_there.html", {"name": name, "date": datetime.now()}
    )

@login_required
@transaction.atomic
def search_by_id(request):  #searches the database for a specific id number
    id_number = request.GET.get('Id_number') #gets the id number from the search bar
    if id_number: #if the id number exists
        checkin = db_model.objects.filter(id_number=id_number).first() #first() returns the first object matched by the queryset
    else: #if the id number does not exist
        checkin = False #set checkin to false
    context = {'Checkin': checkin} #context is a dictionary that maps variable names to objects
    return render(request, 'hello/id_search_results.html', context) #renders the id search results page

@login_required
@transaction.atomic
def add_entry(request):
    if request.method == 'POST':
        # Retrieve form data
        company_name = request.POST.get('company_name')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        alumni = bool(request.POST.get('alumni'))
        release_info = bool(request.POST.get('release_info'))
        id_number = request.POST.get('id_number')
        table_number = request.POST.get('table_number')

        # Perform form validation
        errors = {}

        if not company_name.isalpha():
            errors['company_name'] = 'Please enter a valid company name.'

        if not first_name.isalpha():
            errors['first_name'] = 'Please enter a valid first name.'

        if not last_name.isalpha():
            errors['last_name'] = 'Please enter a valid last name.'

        if not email:
            errors['email'] = 'Please enter a valid email address.'

        if not id_number.isdigit():
            errors['id_number'] = 'Please enter a valid ID number.'
        
        if not table_number.isdigit():
            errors['table_number'] = 'Please enter a valid table number.'

        # If there are errors, render the form with error messages
        if errors:
            return render(request, 'hello/add_entry.html', {'errors': errors})

        # Create an instance of db_model model and set the field values
        checkin_entry = db_model(
            company_name=company_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            alumni=alumni,
            release_info=release_info,
            id_number=int(id_number),
            checked_in=True,
            checked_in_time=timezone.now(),  # Autopopulate with current time and date,
            table_number=table_number,
            email_sent=False,
        )


        # Save the instance to the database
        checkin_entry.save()

        return redirect('/success')  # Redirect to a success page

    return render(request, 'hello/add_entry.html')


@login_required
@transaction.atomic
def update_entry(request):
    if request.method == 'POST':
        # Retrieve form data
        id_number = request.POST.get('id_number')
        
        # Retrieve the existing entry with the matching ID
        try:
            checkin_entry = db_model.objects.get(id_number=int(id_number))
        except db_model.DoesNotExist:
            # Handle the case when the entry does not exist
            return render(request, 'hello/error.html')
        
        # Update the field values of the existing entry
        checkin_entry.company_name = request.POST.get('company_name')
        checkin_entry.first_name = request.POST.get('first_name')
        checkin_entry.last_name = request.POST.get('last_name')
        checkin_entry.email = request.POST.get('email')
        checkin_entry.alumni = bool(request.POST.get('alumni'))
        checkin_entry.release_info = bool(request.POST.get('release_info'))
        checkin_entry.checked_in = True
        checkin_entry.checked_in_time=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),  # Autopopulate with current time and date,
        
        # Save the updated entry to the database
        checkin_entry.save()
        table_number = checkin_entry.table_number
    return HttpResponseRedirect(reverse('success') + f'?table_number={table_number}')
    



@login_required
def db_display(request, page=1): #this function displays all of the entries in the database
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT * FROM Master_list") #displaying all entries in the Master_list table
        rows = cursor.fetchall() 
    converted_rows = []
    for row in rows:
        converted_row = list(row)
        # Convert 'alumni' field
        converted_row[4] = 'yes' if converted_row[4] == 1 else 'no'
        # Convert 'release_info' field
        converted_row[5] = 'yes' if converted_row[5] == 1 else 'no'
        # Convert 'checked_in' field
        converted_row[7] = 'yes' if converted_row[7] == 1 else 'no'
        # Convert 'email_sent' field
        converted_row[10] = 'yes' if converted_row[10] == 1 else 'no'
        converted_rows.append(converted_row)

    paginator = Paginator(converted_rows, 100) #the number determines how many entries are displayed per page
    page_obj = paginator.get_page(page)

    url = reverse('db_display', args=[page],)  # Get the URL for the current page
    return render(request, "hello/db_display.html", {'page_obj': page_obj, 'url': url})


@login_required
@transaction.atomic
def search_by_id(request):
    context = {}
    if 'id_number' in request.GET:
        messages.info(request, 'You searched for: {}'.format(request.GET['id_number']))
        id_number = request.GET['id_number']
        try:
            entry = db_model.objects.get(id_number=id_number)
            context['entry'] = entry
            messages.success(request, 'Entry found.')
        except db_model.DoesNotExist:
            messages.error(request, 'There is no corresponding entry for that number.')
            return render(request, 'hello/search.html', context)

    return render(request, 'hello/search.html', context)


def homepage(request):
    return render(request, 'hello/home.html')



#below is the code for the apple wallet pass




def generate_pass(request, id_number):
    try:
        primary_entry = db_model.objects.get(id_number=id_number)
        
        pass_instance, created = Pass.objects.get_or_create(serial_number=id_number)  # Use id_number as serial_number
        
        pass_data = {
            "serialNumber": pass_instance.serial_number,
            # Add more pass data fields as needed
        }
        
        response = HttpResponse(content_type="application/vnd.apple.pkpass")
        response["Content-Disposition"] = f'attachment; filename="{id_number}.pkpass"'
        
        pass_path = pass_instance.generate_pass(pass_data)
        
        with open(pass_path, "rb") as f:
            response.write(f.read())
        
        return response
    except db_model.DoesNotExist:
        return HttpResponse("Pass not found", status=404)