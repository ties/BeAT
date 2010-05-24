import os
import sys

sys.path.append('/var/www/django/BeAT/')
sys.path.append('/var/www/django/BeAT/beat')

os.environ['DJANGO_SETTINGS_MODULE'] = 'beat.settings'
os.environ['HOME'] = '/var/www/django/BeAT/cwd'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
