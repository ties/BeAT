from django.db import models

class Model(models.Model):	
	name = models.CharField(max_length=200)
	version = models.CharField(max_length=50)
	location = models.FilePathField(path="site_media/models")
	
	def __unicode__(self):
		return self.name + '.' + self.version
	
	#function so that the serializers put the name and version in the json instead of the foreign key
	def natural_key(self):
		return (self.name,self.version)
	
	#plug user management here by adding a link to an entry in a table containing usernames

class Tool(models.Model):	
	name = models.CharField(max_length=200)
	version = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name + ' ' + self.version

class BenchmarkOption(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	option = models.ForeignKey('Option')

class Option(models.Model):
	name = models.CharField(max_length=50)
	value = models.CharField(max_length=100)
	
	def __unicode__(self):
		return u'-' + self.name + '=' + self.value
	
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

class Benchmark(models.Model):
	#Idenifying elements
	model_ID = models.ForeignKey('Model')
	tool_ID = models.ForeignKey('Tool')
	hardware_ID = models.ManyToManyField('Hardware', through="BenchmarkHardware", verbose_name="hardware")
	option_ID = models.ManyToManyField('Option', through="BenchmarkOption", verbose_name="option")
	date_time = models.DateTimeField('Time started')
	#Data
	user_time = models.FloatField(verbose_name="User time (s)")
	system_time = models.FloatField(verbose_name="System time (s)")
	elapsed_time = models.FloatField(verbose_name="Elapsed time (s)")

#	fix this one later
#	finished = models.BooleanField(verbose_name="Run successfully finished?")
	
	transition_count = models.BigIntegerField(verbose_name="Transitions", null=True) #this may be null
	states_count = models.BigIntegerField(verbose_name="States")
	memory_VSIZE = models.IntegerField(verbose_name="Memory VSIZE (KB)") #rounded to kilobytes
	memory_RSS = models.IntegerField(verbose_name="Memory RSS (KB)")	#rounded to kilobytes
	
	def __unicode__(self):
		return self.model_ID.__str__() + '-' + self.tool_ID.name.__str__()