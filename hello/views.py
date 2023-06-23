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


@transaction.atomic
def search_by_id(request):  #searches the database for a specific id number
    id_number = request.GET.get('Id_number') #gets the id number from the search bar
    if id_number: #if the id number exists
        checkin = db_model.objects.filter(id_number=id_number).first() #first() returns the first object matched by the queryset
    else: #if the id number does not exist
        checkin = None #set checkin to None
    context = {'Checkin': checkin} #context is a dictionary that maps variable names to objects
    return render(request, 'hello/id_search_results.html', context) #renders the id search results page

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
        checkin_entry.checked_in = bool(request.POST.get('checked_in'))
        checkin_entry.checked_in_time=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),  # Autopopulate with current time and date,
        
        # Save the updated entry to the database
        checkin_entry.save()
        table_number = checkin_entry.table_number
    return HttpResponseRedirect(reverse('success') + f'?table_number={table_number}')
    




def db_display(request, page=1): #this function displays all of the entries in the database
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT * FROM Master_list") #displaying all entries in the Master_list table
        rows = cursor.fetchall()
    
    paginator = Paginator(rows, 100) #the number determines how many entries are displayed per page
    page_obj = paginator.get_page(page)

    url = reverse('db_display', args=[page],)  # Get the URL for the current page
    return render(request, "hello/db_display.html", {'page_obj': page_obj, 'url': url})


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


