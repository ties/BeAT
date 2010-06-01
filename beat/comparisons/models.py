from django.db import models
from django.contrib.auth.models import User
from beat.tools.hash import hash
from beat.settings import *

class Comparison(models.Model):
	user = models.ForeignKey(User, related_name="owner_c")
	name = models.CharField(max_length=255)
	date_time = models.DateTimeField(verbose_name="Last edit",auto_now=True,auto_now_add=True)
	hash = models.CharField(max_length=40)
	
	algorithm_tool_a = models.ForeignKey('benchmarks.AlgorithmTool', related_name='at_a')
	algorithm_tool_b = models.ForeignKey('benchmarks.AlgorithmTool', related_name='at_b')
	optionvalue = models.ForeignKey('benchmarks.OptionValue', blank=True, null=True)	
	
	def getHash(self):
		return  hash(str(self.id) + str(self.date_time))

	def __unicode__(self):
		return "%s" % (self.name)

class ModelComparison(models.Model):
	TRANSITIONS 	= 'transitions'
	STATES 			= 'states'
	VSIZE 			= 'memory_VSIZE'
	RSS 			= 'memory_RSS'
	ELAPSED_TIME 	= 'elapsed_time'
	TOTAL_TIME 		= 'total_time'
	
	DATA_TYPES = (
		(TRANSITIONS, 'Transition count'),
		(STATES, 'States count'),
		(VSIZE, 'Memory VSIZE'),
		(RSS, 'Memory RSS'),
		(ELAPSED_TIME, 'Elapsed Time'),
		(TOTAL_TIME, 'Total Time'),
	)
	user = models.ForeignKey(User, related_name="owner_mc")
	type = models.CharField(max_length=20, choices=DATA_TYPES)
	tool = models.ForeignKey('benchmarks.Tool')
	algorithm = models.ForeignKey('benchmarks.Algorithm')
	optionvalue = models.ForeignKey('benchmarks.OptionValue', blank=True, null=True)
	date_time = models.DateTimeField(verbose_name="Last edit",auto_now=True,auto_now_add=True)
	name = models.CharField(max_length=255)
	hash = models.CharField(max_length=27)
	#exclude_ids = models.CommaSeparatedIntegerField(max_length=255, blank=True)
	
	def get_absolute_url(self):
		return "/compare/model/%i/" % self.id

	def getHash(self):
		return  hash(str(self.id) + str(self.date_time))
	
	def __unicode__(self):
		return "%s" % (self.name)

