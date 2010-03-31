from django.db import models
from django.contrib.auth.models import User

class Model(models.Model):
	name = models.CharField(max_length=200)
	version = models.CharField(max_length=50)
	location = models.FilePathField(path="site_media/models")
	
	def __unicode__(self):
		return self.name + '.' + self.version
	
	#function so that the serializers put the name and version in the json instead of the foreign key
	def natural_key(self):
		return (self.name,self.version)

class Comparison(models.Model):
	user = models.ForeignKey(User)
	benchmarks = models.CommaSeparatedIntegerField(max_length=255)
	date_time = models.DateTimeField(verbose_name="Last edit",auto_now=True,auto_now_add=True)
	
	def __unicode__(self):
		return self.user.__str__() + '-' + self.benchmarks

class OptionValue(models.Model):
	benchmark = models.ManyToManyField('Benchmark')
	option = models.ForeignKey('Option')
	value = models.CharField(max_length=100)
	def __unicode__(self):
		return "%s = %s"%(self.option.name, self.value)

	
class Option(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class Benchmark(models.Model):
	#Idenifying elements
	model = models.ForeignKey('Model')
	tool = models.ForeignKey('Tool')
	algorithm = models.ForeignKey('Algorithm')
	hardware = models.ManyToManyField('Hardware', through="BenchmarkHardware")
	date_time = models.DateTimeField(verbose_name="Time started")
	
	#Data
	user_time = models.FloatField(verbose_name="User time (s)")
	system_time = models.FloatField(verbose_name="System time (s)")
	elapsed_time = models.FloatField(verbose_name="Elapsed time (s)")
	transition_count = models.BigIntegerField(verbose_name="Transitions", blank=True, null=True) #this may be null
	states_count = models.BigIntegerField(verbose_name="States")
	memory_VSIZE = models.IntegerField(verbose_name="Memory VSIZE (KB)") #rounded to kilobytes
	memory_RSS = models.IntegerField(verbose_name="Memory RSS (KB)") #rounded to kilobytes
	finished = models.BooleanField(verbose_name="Run finished")
	
	total_time = models.FloatField(verbose_name="User + System time (s)")
	
	def __unicode__(self):
		return self.model.__str__() + '-' + self.tool.name.__str__()

class Hardware(models.Model):
	name = models.CharField(max_length=200) 
	memory = models.BigIntegerField(verbose_name="memory (KB)")
	cpu = models.CharField(max_length=200, verbose_name="CPU name")
	disk_space = models.BigIntegerField(verbose_name="disk space (KB)")
	os = models.CharField(max_length=200, verbose_name="operating system")

	def __unicode__(self):
		return self.name + ' @' + str(self.memory) + 'KB RAM, ' + self.cpu + ', ' + self.os
	
	class Meta:
		verbose_name_plural = "Hardware"

class BenchmarkHardware(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	hardware = models.ForeignKey('Hardware')
	
	class Meta:
		verbose_name_plural = "Benchmark Hardware"

class ExtraValue(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	name = models.CharField(max_length=200)
	value = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name + ' ' + self.value

class Tool(models.Model):	
	name = models.CharField(max_length=200)
	version = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name + ' ' + self.version

class ValidOption(models.Model):
	algorithm_tool = models.ForeignKey('AlgorithmTool')
	option = models.ForeignKey('Option')
	regex = models.ForeignKey('Regex')
	
	def __unicode__(self):
		return "%s with option %s" %(self.algorithm_tool.tool.name, self.option.name)

class AlgorithmTool(models.Model):
	algorithm = models.ForeignKey('Algorithm')
	tool = models.ForeignKey('Tool')
	regex = models.ForeignKey('Regex')
	
	def __unicode__(self):
		return self.tool.name + "-" + self.algorithm.name
	
class Algorithm(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
	
class Regex(models.Model):
	regex = models.CharField(max_length=500)

	def __unicode__(self):
		return self.regex

	class Meta:
		verbose_name_plural = "Regexes"

class RegisteredShortcut(models.Model):
	algorithm_tool = models.ForeignKey('AlgorithmTool')
	option = models.ForeignKey('Option')
	shortcut = models.CharField(max_length=1)