from django.urls import path
from django.contrib import admin
from hello import views
from django.contrib.auth import views as auth_views
from django.urls import include
#from .views import generate_pass


urlpatterns = [
  path("", views.homepage, name="home"),
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
  path('accounts/login/', auth_views.LoginView.as_view(template_name='hello/registration/login.html'), name='login'),
  path('qr_email_page/', views.qr_email_page, name='qr_email_page'),
  path('qr_email_page/send_qr_code/', views.send_qr_email, name='send_qr_code'),
  path('qr_email_success/', views.qr_email_success, name='qr_email_success'),
  path('add_new_data/', views.add_new_data, name='add_new_data'),
  path('export/', views.export_data, name='export_data'),
  path('admin/', admin.site.urls),
  path('dbbackup/', views.redirect_w_backup, name='dbbackup'),
  path('self_registration/', views.self_registration, name='self_registration'),
  path('self_reg_success/', views.self_reg_success, name='self_reg_success'),
]
