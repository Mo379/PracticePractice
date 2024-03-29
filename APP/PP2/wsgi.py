"""
WSGI config for PP2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/var/www/html/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PP2.settings')

application = get_wsgi_application()
