from django.urls import path
from django.contrib import admin
from hello import test_settings, views
from django.contrib.auth import views as auth_views
from django.urls import include
# from .views import generate_pass
from hello import test_settings, production_settings


urlpatterns = [
    path("", views.homepage, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("add_entry/", views.add_entry, name="add_entry"),
    path('dbdisplay/<int:page>/', views.db_display, name='db_display'),
    path("dbsearch/", views.search_by_id, name="id_search"),
    path('search_by_id/', views.search_by_id, name='search_by_id'),
    path('on_site_entry_success/', views.on_site_entry_success,
         name='on_site_entry_success'),
    path('QR_entry_success/', views.QR_entry_success, name='QR_entry_success'),
    path('submit-form/', views.update_entry, name='submit_form'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='hello/registration/login.html'), name='login'),
    path('qr_email_page/', views.qr_email_page, name='qr_email_page'),
    # path('qr_email_page/send_qr_code/', views.send_qr_emails, name='send_qr_code'),
    # Add the URL pattern for the email configuration page
    path('email_configuration/', views.email_sending_status, name='email_configuration_page'),
    # Add the URL pattern for updating the email sending status
    #path('update_email_sending_status/', views.update_email_sending_status, name='update_email_sending_status'),
    path('add_new_data/', views.add_new_data, name='add_new_data'),
    path('export/', views.export_data, name='export_data'),
    path('admin/', admin.site.urls),
    path('dbbackup/', views.redirect_w_backup, name='dbbackup'),
    path('self_registration/', views.self_registration, name='self_registration'),
    path('self_reg_success/', views.self_reg_success, name='self_reg_success'),
]


if test_settings.DEBUG or production_settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        # ...
    ] + urlpatterns
