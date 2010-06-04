from django.db import models
from django.contrib.auth.models import User
from beat.settings import *

class JobsFilter(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	tool = models.ForeignKey('benchmarks.Tool')
	algorithm = models.ForeignKey('benchmarks.Algorithm')
	model = models.ForeignKey('benchmarks.Model')
	date_time = models.DateTimeField(verbose_name="Last edit",auto_now=True,auto_now_add=True)
	
	def __unicode__(self):
		return "%s" % (self.user)