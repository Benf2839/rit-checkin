from django.urls import path

from hello import views
from hello.models import LogMessage
from django.contrib.auth import views as auth_views
from django.urls import include

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
    path("add_entry/", views.add_entry, name="add_entry"),
    path('dbdisplay/<int:page>/', views.db_display, name='db_display'),
    path("dbsearch/", views.search_by_id, name="id_search"),
    path('search_by_id/', views.search_by_id, name='search_by_id'),
    path('success/', views.success, name='success'),
    path('submit-form/', views.update_entry, name='submit_form'),
    path('accounts/', include('django.contrib.auth.urls')),
    ]
