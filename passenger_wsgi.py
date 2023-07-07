import sys
import os

# Add your project's virtual environment path
# Replace '/path/to/venv' with the actual path
project_base = '.venv'
python_version = 'python3.11.2'

sys.path.append(project_base)
sys.path.append(os.getcwd())
sys.executable = os.path.join(project_base, 'bin', python_version)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
