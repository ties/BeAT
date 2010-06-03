from django.db import models
from django.contrib.auth.models import User

class JobsFilter(models.Model):
	user = models.ForeignKey(User)
	tool = models.ForeignKey('benchmarks.Tool')
	algorithm = models.ForeignKey('benchmarks.Algorithm')
	
	def __unicode__(self):
		return "%s" % (self.user)