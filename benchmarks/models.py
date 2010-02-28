from django.db import models

class Model(models.Model):	
	Name = models.CharField(max_length=200)
	Version = models.CharField(max_length=50)
	Location = models.FilePathField(path="site_media/models") #example path for storing all models; required for FilePathField
	
	def __unicode__(self):
		return self.Name + '.' + self.Version
	
	#plug user management here by adding a link to an entry in a table containing usernames

class Tool(models.Model):	
	Name = models.CharField(max_length=200)
	Version = models.CharField(max_length=50)
	Option = models.ManyToManyField('Option', through='ToolOption')
	
	def __unicode__(self):
		return self.Name + ' ' + self.Version

class ToolOption(models.Model):
	tool = models.ForeignKey('Tool')
	option = models.ForeignKey('Option')

class Option(models.Model):
	Name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return u'-' + self.Name
	
class Hardware_Profile(models.Model):
	Name = models.CharField(max_length=200)
	Hardware = models.ManyToManyField('Hardware')
	
	def __unicode__(self):
		return self.Name
		
	class Meta:
		verbose_name = "Hardware Profile"
		verbose_name_plural = "Hardware Profiles"
		
class Hardware(models.Model):
	Name = models.CharField(max_length=200) #placeholder, should be replaced by a many2many relation in order to make a list of hardware

	def __unicode__(self):
		return self.Name
		
	class Meta:
		verbose_name_plural = "Hardware"

class FactTable(models.Model):
	#Idenifying elements
	Model_ID = models.ForeignKey('Model')
	Tool_ID = models.ForeignKey('Tool')
	Hardware_ID = models.ForeignKey('Hardware_Profile')
	Date_time = models.DateTimeField('Time started')
	#Data
	Run_time = models.BigIntegerField()
	Transition_count = models.BigIntegerField()
	States_count = models.BigIntegerField()
	Memory_used = models.IntegerField() #rounded to kilobytes
	
	def __unicode__(self):
		return self.Model_ID.__unicode__() + '-' + self.Tool_ID.Name.__unicode__()