Welcome to the repo for the RIT Career Services & Co-Op check-in system website

To run the website locally, follow these steps:

1. Create a virtual environment within your IDE.
2. Activate the virtual environment by running `source env/bin/activate` (Linux/MacOS) or `env\scripts\activate` (Windows).
3. There is a requirements.txt file that should have all of the necessary packages. You can use `pip install -r requirements.txt`.
4. To run in development mode, make sure that the manage.py file specifies 'hello.test_settings' as I created two settings files for testing.

- Within the test settings file, there are two database configurations. The first is for the SQLite database, and the second is for the PostgreSQL database. The SQLite database is used for testing locally, and the PostgreSQL database is for testing with data directly from the server. To get access to the postgres database, I will need to add your IP address to the whitelist and create an account for you.

5. Once that has been done, you can run the server by running `python manage.py runserver`.

- The login credentials for the admin page are:
  - Username: oce
  - Password: test
