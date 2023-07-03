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
from io import TextIOWrapper
from .forms import EntryForm
from django.contrib import messages
from hello.models import db_model
import re




# Define the regular expression patterns
name_pattern = r'^[A-Za-z -]+$'  # Only alphabetic characters, spaces, and dashes
email_pattern = r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'  # Valid email pattern



@transaction.atomic
def add_new_data(request):
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
            
            form = EntryForm(request.POST, request.FILES) # Create a form instance and populate it with data from the request
            messages.success(request, 'form exists')
           # if form.is_valid():
            # Retrieve the uploaded file from the form
            file = request.FILES['file']
            messages.success(request, 'form is valid')
            
            master_list = db_model.objects.all()
            # Prepare CSV data
            csv_data = []
            csv_data.append(['Company_name', 'First_name', 'Last_name', 'Email', 'Alumni', 'Release_info', 'Checked_in', 'Checked_in_time', 'Table_number', 'id_number'])

            for entry in master_list:
                csv_data.append([
                    entry.company_name, entry.first_name, entry.last_name, entry.email, entry.alumni, entry.release_info, entry.checked_in,
                    entry.checked_in_time, entry.table_number, entry.id_number
                ])

            # Create a CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Master_list_backup.csv"'

            # Write CSV data to the response
            writer = csv.writer(response)
            writer.writerows(csv_data)

            messages.success(request, 'Data exported successfully.')
            
            # Wipe the Master_list table
            db_model.objects.all().delete()

            # Process the uploaded CSV file
            try:
                # Decode the uploaded file
                csv_file = TextIOWrapper(file, encoding='utf-8')


                textbox0_value = request.POST.get('Company_Name_box')
                textbox1_value = request.POST.get('First_Name_box')
                textbox2_value = request.POST.get('Last_Name_box')
                textbox3_value = request.POST.get('Email_box')
                textbox4_value = request.POST.get('Alumni_box')
                textbox5_value = request.POST.get('Release_info_box')
                textbox6_value = request.POST.get('Table_number_box')

                if textbox0_value or textbox1_value or textbox2_value or textbox3_value or textbox4_value or textbox5_value or textbox6_value:
                    # Convert box numbers from letters to numbers
                    box_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15}
                    textbox0_value = box_mapping.get(textbox0_value.lower()) if textbox0_value  else None
                    textbox1_value = box_mapping.get(textbox1_value.lower()) if textbox1_value  else None
                    textbox2_value = box_mapping.get(textbox2_value.lower()) if textbox2_value  else None
                    textbox3_value = box_mapping.get(textbox3_value.lower()) if textbox3_value  else None
                    textbox4_value = box_mapping.get(textbox4_value.lower()) if textbox4_value  else None
                    textbox5_value = box_mapping.get(textbox5_value.lower()) if textbox5_value  else None
                    textbox6_value = box_mapping.get(textbox6_value.lower()) if textbox6_value  else None
                    messages.success(request, 'textbox values converted to numbers')
                
                else:
                    messages.error(request, 'please enter a valid letter in all textboxes')




                # Read the CSV data
                reader = csv.reader(csv_file)
                reader.__next__()  # Skip the header row
                for row in reader:
                    # Extract the data from each row
                    ext_company_name = row[textbox0_value]  
                    ext_first_name = row[textbox1_value]
                    ext_last_name = row[textbox2_value]
                    ext_email = row[textbox3_value]
                    ext_alumni = row[textbox4_value]
                    ext_release_info = row[textbox5_value]
                    ext_table_number = row[textbox6_value]

                    # Check if all required fields are empty (excluding company_name)
                    if not ext_first_name or ext_last_name or ext_email or ext_alumni or ext_release_info:
                        break  # Stop iterating over rows

                    # Perform validations on the data
                    errors = []
                    if ext_company_name and not re.match(name_pattern, ext_company_name):
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
                        errors.append('Incorrect format for release info')

                    # If there are any errors, render the current page with the error messages
                    if errors:
                        return render(request, 'database_upload_page.html', {'errors': errors})

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
                        company_name=ext_company_name,
                        first_name=ext_first_name,
                        last_name=ext_last_name,
                        email=ext_email,
                        alumni=ext_alumni,
                        release_info=ext_release_info,
                        table_number=ext_table_number
                    )
                    entry.save()

                messages.success(request, 'Data imported successfully.')
                return redirect(add_new_data, response)
            
            except Exception as e: # Handle any other exceptions
                messages.error(request, f'Error processing the CSV file: {str(e)}') # Display the exception as an error message
            return redirect('add_new_data') # Redirect to the database upload page
    
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
        # Get the ID number from the POST data
        id_number = request.POST.get("id_number")
        # Retrieve the corresponding record from the database based on the ID number
        record = get_object_or_404(db_model, id_number=id_number)
        
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = request.POST.get("Here is your QR code for check-in")
            email_from = settings.EMAIL_HOST_USER
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

            # Send the email
            EmailMessage(subject, email_content, email_from, recipient_list, connection=connection).send()

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
            table_number=table_number
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
    
    paginator = Paginator(rows, 100) #the number determines how many entries are displayed per page
    page_obj = paginator.get_page(page)

    url = reverse('db_display', args=[page],)  # Get the URL for the current page
    return render(request, "hello/db_display.html", {'page_obj': page_obj, 'url': url})


@login_required
@transaction.atomic
def search_by_id(request):
    context = {}
    if 'id_number' in request.GET:
        id_number = request.GET['id_number']
        try:
            entry = db_model.objects.get(id_number=id_number)
            context['entry'] = entry
        except db_model.DoesNotExist:
            messages.error(request, 'There is no corresponding entry for that number.')
            return render(request, 'hello/search.html', context)

    return render(request, 'hello/search.html', context)


