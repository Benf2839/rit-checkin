from django.db import models
from django.utils import timezone

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"


class db_model(models.Model): #creates a model for the checkin database
    id_number = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    alumni = models.BooleanField(default=False)
    release_info = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    checked_in_time = models.DateTimeField(auto_now=True)
    table_number = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'Master_list'

    def __str__(self):
        return f"{self.company_name} - {self.first_name} - {self.last_name} - {self.email} - {self.alumni} - {self.release_info} - {self.id_number} - {self.checked_in} - {self.checked_in_time} - {self.table_number}"
