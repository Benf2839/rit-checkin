from django.urls import path

from hello import views
from hello.models import LogMessage

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="hello/home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_message, name="log"),
    path("search/", views.search_results, name="search_results"),
    path('dbdisplay/<int:page>/', views.db_display, name='db_display'),
    path("dbsearch/", views.id_search_page, name="id_search_page"),
    path('search_by_id/', views.search_by_id, name='search_by_id'),
    ]
