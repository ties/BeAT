from beat.benchmarks.models import *
from beat.comparisons.models import *
from django.contrib import admin

class HardwareInline(admin.TabularInline):
	model = BenchmarkHardware
	extra = 1

class OptionValueInline(admin.TabularInline):
	model = BenchmarkOptionValue
	extra = 1

class AlgorithmToolInline(admin.TabularInline):
	model = AlgorithmTool
	extra = 1
	
class BenchmarkAdmin(admin.ModelAdmin):
	list_display = ('model', 'algorithm_tool', 'date_time', 'finished', 'user_time', 'system_time', 'total_time', 'elapsed_time', 'memory_VSIZE', 'memory_RSS', 'states_count', 'transition_count')
	list_filter = ['date_time']
	search_fields = ['model__name', 'algorithm_tool__tool__name', 'algorithm_name__algorithm__name']
	fieldsets = [
		('Configuration', {'fields': ['model','algorithm_tool','finished']}),
		('Date information', {'fields': ['date_time']}),
		('Output data', {'fields': ['user_time', 'system_time','total_time', 'elapsed_time','transition_count','states_count','memory_VSIZE', 'memory_RSS', 'logfile']}),
	]
	inlines = [HardwareInline, OptionValueInline]

class ValidOptionInline(admin.TabularInline):
	model = ValidOption
	extra = 1

class AlgorithmToolAdmin(admin.ModelAdmin):
	inlines=[
		ValidOptionInline,
	]
	
admin.site.register(Model)
#admin.site.register(Tool, ToolAdmin)
admin.site.register(Tool)
#admin.site.register(Tool)
admin.site.register(Regex)
admin.site.register(Hardware)
admin.site.register(Option)
admin.site.register(Benchmark, BenchmarkAdmin)
#admin.site.register(Benchmark)
admin.site.register(Comparison)
admin.site.register(ModelComparison)
admin.site.register(Algorithm)
admin.site.register(RegisteredShortcut)
admin.site.register(ExtraValue)
admin.site.register(AlgorithmTool, AlgorithmToolAdmin)

admin.site.register(ValidOption)
admin.site.register(OptionValue)
admin.site.register(BenchmarkOptionValue)
