from beat.benchmarks.models import *
from django.core import management
from django.db.models import get_app

management.call_command('flush', verbosity=0, interactive=False)
management.call_command('loaddata', 'big_set.json', verbosity=0)
