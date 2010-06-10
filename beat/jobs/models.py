from django.db import models
from django.contrib.auth.models import User
from beat.settings import *

class JobsFilter(models.Model):
	# 'Administrative' data
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	date_time = models.DateTimeField(verbose_name="Last edit",auto_now=True,auto_now_add=True)
	# Job data
	nodes = models.CharField(max_length=255)
	tool = models.ForeignKey('benchmarks.Tool')
	algorithm = models.ForeignKey('benchmarks.Algorithm')
	options = models.CharField(max_length=255)
	model = models.ForeignKey('benchmarks.Model')
	prefix = models.CharField(max_length=255)
	postfix = models.CharField(max_length=255)
	
	
	def __unicode__(self):
		return "%s" % (self.name)