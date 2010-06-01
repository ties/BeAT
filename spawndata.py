from beat.benchmarks.models import *
import random
from decimal import Decimal
from datetime import datetime

def varieer(time):
	return Decimal(str(time * random.random()*(0.2 + 0.9)))

b = Benchmark.objects.all()
for i in b:
	at = i.algorithm_tool
	x = at.date
	somedate = datetime(x.year, (x.month+1+(random.random() < 0.5))%12+1, (x.day+1+(random.random() < 0.5))%28+1, x.hour, x.minute, x.second)
	at, c = AlgorithmTool.objects.get_or_create(tool=at.tool, algorithm=at.algorithm, version=at.version[-59:]+'1', regex=at.regex, date=somedate)
	h = i.hardware.all()
	o = i.optionvalue.all()
	i.user_time = Decimal(varieer(i.user_time))
	i.system_time = Decimal(varieer(i.system_time))
	i.elapsed_time = Decimal(varieer(i.elapsed_time))
	i.total_time = i.user_time + i.system_time + i.elapsed_time
	bench, c = Benchmark.objects.get_or_create(model=i.model, algorithm_tool=at, date_time=i.date_time, defaults={'user_time':i.user_time,
				'system_time':i.system_time,'elapsed_time':i.elapsed_time,
				'total_time':i.total_time,
				'transition_count':i.transition_count, 'states_count':i.states_count,
				'memory_VSIZE':i.memory_VSIZE, 'memory_RSS':i.memory_RSS, 'finished':i.finished})
	
	for x in h:
		bh, c = BenchmarkHardware.objects.get_or_create(hardware=x, benchmark=bench)
	for x in o:
		bov, c = BenchmarkOptionValue.objects.get_or_create(optionvalue=x, benchmark=bench)

	
	
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
