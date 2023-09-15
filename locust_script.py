from locust import HttpUser, task, between
import random
import string


class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks

    @task
    def enter_info_and_submit(self):
        # Generate random data for form fields (modify as needed)
        first_name = ''.join(random.choices(string.ascii_letters, k=8))
        last_name = ''.join(random.choices(string.ascii_letters, k=8))
        email = f"{first_name.lower()}_{last_name.lower()}@example.com"

        # Define the data to be submitted in the POST request
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'alumni': False,
            'release_info': False
            # Add other form fields and their values here
        }

        # Send a POST request to submit the form
        self.client.post("https://eventcheck-in.com/add_entry/", data=data)
