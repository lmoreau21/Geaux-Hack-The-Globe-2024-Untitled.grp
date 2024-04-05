"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
#Paul: Wikipedia says that 
# The Web Server Gateway Interface (WSGI, pronounced whiskey[1][2] or WIZ-ghee[3]) 
# is a simple calling convention for web servers to forward requests to web applications 
# or frameworks written in the Python programming language. 
# The current version of WSGI, version 1.0.1, is specified in Python Enhancement Proposal (PEP) 3333.[4]