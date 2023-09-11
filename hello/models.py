from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
#from django_walletpass.models import Pass, PassFile, PassBuilder
#from django_walletpass import settings as pass_settings



class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"

class import_csv(models.Model): #creates a model for the import .csv file format
    id_number = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email = models.EmailField()
    alumni = models.BooleanField(default=False)
    release_info = models.BooleanField(default=False)
    table_number = models.IntegerField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} - {self.first_name} - {self.last_name} - {self.email} - {self.alumni} - {self.release_info} - {self.id_number} - {self.table_number} - {self.email_sent}"


class db_model(models.Model): #creates a model for the checkin database
    id_number = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField()
    alumni = models.BooleanField(null=True)
    release_info = models.BooleanField(null=True)
    checked_in = models.BooleanField(default=False)
    checked_in_time = models.DateTimeField(auto_now=True)
    table_number = models.IntegerField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    class Meta:
        db_table = 'Master_list'

    def __str__(self):
        return f"{self.company_name} - {self.first_name} - {self.last_name} - {self.email} - {self.alumni} - {self.release_info} - {self.id_number} - {self.checked_in} - {self.checked_in_time} - {self.table_number} - {self.email_sent}"


class Pass(models.Model):
    serial_number = models.CharField(max_length=100)
    pass_instance = models.ForeignKey(db_model, on_delete=models.CASCADE) #creates a foreign key to the db_model
    

    @receiver(post_save, sender=db_model)
    def create_or_update_pass(sender, instance, created, **kwargs): #creates a pass for each entry in the db_model
        if created:
            pass_instance, _ = Pass.objects.get_or_create(pass_instance=instance)
            # Copy id_number to serial_number in Pass instance
            pass_instance.serial_number = instance.id_number
            pass_instance.save()
        else:
            pass_instance, _ = Pass.objects.get_or_create(pass_instance=instance)
            # Update pass_instance with any additional information if needed

    post_save.connect(create_or_update_pass, sender=db_model) #connects the create_or_update_pass function to the db_model


#    def generate_pass(self, pass_data):
#        # Get the pass generator
#        pass_generator = PassBuilder()
#
#        # Create a Pass object
#        pass_instance, created = Pass.objects.get_or_create(serial_number=self.id_number)  # Set serial_number to id_number
 #       
#        # Set pass data fields
#        pass_instance.pass_type_identifier = ""
#        # Set other pass data fields as needed
#        id_number = pass_data['id_number'] #gets the id_number from the db_model
#        pass_generator.pass_data.update({
#            "barcode": {
#                "message": id_number,
#                "format": "PKBarcodeFormatPDF417",
#                "messageEncoding": "iso-8859-1"
#            },
#            "organizationName": "Organic Produce",
#            "description": "Organic Produce Loyalty Card",
#            })
#        # Generate the pass file
#        pass_file = pass_generator.create_pass(pass_instance)
#        
#        # Save the pass file
#        pass_instance.save()
#
#        # Return the path to the generated pass file
#        return pass_file.passfile.path
#    
#