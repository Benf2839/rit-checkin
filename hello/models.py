from django.db import models
from django.utils import timezone

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

class CheckinTest(models.Model): #creates a model for the checkin database
    company_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    alumni = models.BooleanField(default=False)
    release_info = models.BooleanField(default=False)
    id_number = models.IntegerField()
    checked_in = models.BooleanField(default=False)
    checked_in_time = models.DateTimeField(null=True, blank=True)
    table_number = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'Checkin_test'

    def __str__(self):
        return f"{self.company_name} - {self.first_name} - {self.last_name} - {self.email} - {self.alumni} - {self.release_info} - {self.id_number} - {self.checked_in} - {self.checked_in_time} - {self.table_number}"
