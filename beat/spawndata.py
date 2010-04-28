from benchmarks.models import *
import random

def varieer(time):
	return time * (random.random() * 0.2 + 0.9)

b = Benchmark.objects.all()
for i in b:
	t = i.tool
	t, c = Tool.objects.get_or_create(name=t.name,version=int(t.version)+1)
	h = i.hardware.all()
	o = i.optionvalue.all()
	i.user_time = varieer(i.user_time)
	i.system_time = varieer(i.system_time)
	i.elapsed_time = varieer(i.elapsed_time)
	i.total_time = i.user_time + i.system_time + i.elapsed_time
	bench, c = Benchmark.objects.get_or_create(model=i.model, tool=t, algorithm=i.algorithm,
				date_time=i.date_time, defaults={'user_time':i.user_time,
				'system_time':i.system_time,'elapsed_time':i.elapsed_time,
				'total_time':i.total_time,
				'transition_count':i.transition_count, 'states_count':i.states_count,
				'memory_VSIZE':i.memory_VSIZE, 'memory_RSS':i.memory_RSS, 'finished':i.finished})
	bench.save()
	

	
	
"""
class Benchmark(models.Model):
	#Idenifying elements
	model = models.ForeignKey('Model')
	tool = models.ForeignKey('Tool')
	algorithm = models.ForeignKey('Algorithm')
	hardware = models.ManyToManyField('Hardware', through="BenchmarkHardware")
	optionvalue = models.ManyToManyField('OptionValue', through="BenchmarkOptionValue")
	date_time = models.DateTimeField(verbose_name="Time started")
	
	#Data
	user_time = models.FloatField(verbose_name="User time (s)")
	system_time = models.FloatField(verbose_name="System time (s)")
	total_time = models.FloatField(verbose_name="User + System time (s)")
	elapsed_time = models.FloatField(verbose_name="Elapsed time (s)")
	transition_count = models.BigIntegerField(verbose_name="Transitions", blank=True, null=True) #this may be null
	states_count = models.BigIntegerField(verbose_name="States")
	memory_VSIZE = models.IntegerField(verbose_name="Memory VSIZE (KB)") #rounded to kilobytes
	memory_RSS = models.IntegerField(verbose_name="Memory RSS (KB)") #rounded to kilobytes
	finished = models.BooleanField(verbose_name="Run finished")
"""