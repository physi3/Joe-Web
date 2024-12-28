import os

# Set the Django DEBUG environment variable
os.environ['GUNICORN_DEBUG'] = 'True'

# Bind to a specific IP address and port
bind = "0.0.0.0:8080"

# Number of worker processes (adjust based on your server's CPU cores)
workers = 2

# Timeout in seconds (default: 30)
timeout = 30

# Log settings
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log errors to stderr
loglevel = "debug"  # Set log level (debug, info, warning, error, critical)

wsgi_app = "joeweb.wsgi:application"

daemon = False

reload = True  # Automatically reload workers on code changes