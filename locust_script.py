from locust import HttpUser, task, between
import random
import string
import re  # For regular expressions

# use  locust -f locust_script.py  to run the testing


class MyUser(HttpUser):
    wait_time = between(10, 20)  # Wait between 1 and 5 seconds between tasks

    def on_start(self):
        # Perform a GET request to the page to obtain the CSRF token
        response = self.client.get(
            "https://eventcheck-in.com/self_registration/")
        csrf_token = self.extract_csrf_token(
            response.text)  # Extract the CSRF token
        self.csrf_token = csrf_token

    @task
    def enter_info_and_submit(self):
        # Generate random data for form fields (modify as needed)
        first_name = ''.join(random.choices(string.ascii_letters, k=8))
        last_name = ''.join(random.choices(string.ascii_letters, k=8))
        email = f"{first_name.lower()}_{last_name.lower()}@example.com"

        # Define the data to be submitted in the POST request, including the CSRF token
        data = {
            'csrfmiddlewaretoken': self.csrf_token,  # Include the CSRF token here
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'alumni': False,
            'release_info': False
            # Add other form fields and their values here
        }

        # Send a POST request to submit the form
        self.client.post(
            "https://eventcheck-in.com/self_registration/", data=data)

    def extract_csrf_token(self, response_text):
        # Use regular expressions to extract the CSRF token from the HTML response
        csrf_token_match = re.search(
            r'name="csrfmiddlewaretoken" value="(.+?)"', response_text)
        if csrf_token_match:
            return csrf_token_match.group(1)
        else:
            raise ValueError("CSRF token not found in HTML response")
