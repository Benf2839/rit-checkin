from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

# Navigate to the URL
driver.get("https://eventcheck-in.com/self_registration/")

# Extract the CSRF token
csrf_field = driver.find_element(by="name", value="csrfmiddlewaretoken")

# Extract the CSRF token value
csrf_token = csrf_field.get_attribute("value")

# Generate random data for form fields (modify as needed)
first_name = 'John'
compay_name = 'testCompany'
last_name = 'Doe'
email = 'johndoe@example.com'

# Find the form fields and submit button by their HTML attributes (you may need to inspect the HTML source to get the correct attribute values)
company_name_field = driver.find_element(by="name", value="company_name")
first_name_field = driver.find_element(by="name", value="first_name")
last_name_field = driver.find_element(by="name", value="last_name")
email_field = driver.find_element(by="name", value="email")
alumni_checkbox = driver.find_element(by="name", value="alumni")
release_info_checkbox = driver.find_element(by="name", value="release_info")
submit_button = driver.find_element(by="name", value="submit_button")

# Fill in the form fields
first_name_field.send_keys(first_name)
last_name_field.send_keys(last_name)
email_field.send_keys(email)

# If needed, you can include the CSRF token
csrf_field = driver.find_element(by="name", value="csrfmiddlewaretoken")
csrf_field.send_keys(csrf_token)

# Uncheck the "Alumni" and "Release Info" checkboxes (if needed)
if alumni_checkbox.is_selected():
    alumni_checkbox.click()
if release_info_checkbox.is_selected():
    release_info_checkbox.click()

# Submit the form
submit_button.click()

# Quit the WebDriver when done
driver.quit()
