from django.shortcuts import redirect, render
from django.utils.timezone import datetime
from django.views.generic import ListView
from django.db import connections
from hello.forms import LogMessageForm
from hello.models import LogMessage
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from hello.models import CheckinTest



class HomeListView(ListView):
    """Renders the home page, with a list of all logs."""

    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context
    

def about(request):
    """Renders the about page."""
    return render(request, "hello/about.html")


def contact(request):
    """Renders the contact page."""
    return render(request, "hello/contact.html")


def hello_there(request, name):
    """Renders the hello_there page.
    Args:
        name: Name to say hello to
    """
    return render(
        request, "hello/hello_there.html", {"name": name, "date": datetime.now()}
    )


def search_results(request): #searches the database for a specific message
    """Renders the search results page."""
    search_query = request.GET.get('search_query', '')
    logs = LogMessage.objects.filter(message__icontains=search_query)
    context = {
        'search_query': search_query,
        'logs': logs,
    }
    return render(request, "hello/search_results.html", context)


def id_search_page(request): #displays the id search page
    """Renders the id search page."""
    return render(request, 'hello/search_page.html')


def search_by_id(request):  #searches the database for a specific id number
    id_number = request.GET.get('Id_number') #gets the id number from the search bar
    if id_number: #if the id number exists
        checkin = CheckinTest.objects.filter(id_number=id_number).first() #first() returns the first object matched by the queryset
    else: #if the id number does not exist
        checkin = None #set checkin to None
    context = {'Checkin': checkin} #context is a dictionary that maps variable names to objects
    return render(request, 'hello/id_search_results.html', context) #renders the id search results page



def log_message(request):
    form = LogMessageForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
        else:
            return render(request, "hello/log_message.html", {"form": form})
    else:
        return render(request, "hello/log_message.html", {"form": form})
    

def db_display(request, page=1): #this function displays all of the entries in the database
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT * FROM Checkin_test") #displaying all entries in the Checkin_test table
        rows = cursor.fetchall()
    
    paginator = Paginator(rows, 100) #the number determines how many entries are displayed per page
    page_obj = paginator.get_page(page)

    url = reverse('db_display', args=[page],)  # Get the URL for the current page
    return render(request, "hello/db_display.html", {'page_obj': page_obj, 'url': url})


def search_page(request): #displays the search page
    result = None
    if request.method == 'GET' and 'id_number' in request.GET:
        id_number = request.GET['id_number']
        result = search_by_id(id_number)  # assuming you've defined this function to return the row
    return render(request, 'search.html', {'result': result})


