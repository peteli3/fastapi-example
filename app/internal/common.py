from fastapi.templating import Jinja2Templates
import os

templates = Jinja2Templates(directory="app/templates")

# Get version information
VERSION = os.environ.get('VERSION', 'unknown')
GIT_COMMIT = os.environ.get('GIT_COMMIT', 'unknown')