#!/bin/bash

# Change to your Django project directory
cd /home/guardia2/Web_apps

# Activate your virtual environment if needed
source /home/guardia2/virtualenv/Web_apps/3.10/bin/activate && cd /home/guardia2/Web_apps

# Run the send_emails management command
python manage.py send_emails
