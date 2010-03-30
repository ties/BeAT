from beat.benchmarks.models import *
from django.contrib import admin

class HardwareInline(admin.TabularInline):
	model = BenchmarkHardware
	extra = 1

class OptionToolInline(admin.TabularInline):
	model = OptionTool
	extra = 1

class AlgorithmToolInline(admin.TabularInline):
	model = AlgorithmTool
	extra = 1
	
class ToolAdmin(admin.ModelAdmin):
	list_display = ('name', 'version')
	
	inlines = [OptionToolInline, AlgorithmToolInline]
	
class BenchmarkAdmin(admin.ModelAdmin):
	list_display = ('model', 'tool', 'algorithm', 'date_time', 'finished','user_time', 'system_time', 'elapsed_time', 'memory_VSIZE', 'memory_RSS', 'states_count', 'transition_count')
	list_filter = ['date_time']
	search_fields = ['model__name', 'tool__name', 'algorithm__name']
	fieldsets = [
		('Configuration', {'fields': ['model','tool','algorithm','finished']}),
		('Date information', {'fields': ['date_time']}),
		('Output data', {'fields': ['user_time', 'system_time', 'elapsed_time','transition_count','states_count','memory_VSIZE', 'memory_RSS']}),
	]
	inlines = [HardwareInline]

	
	
admin.site.register(Model)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Regex)
admin.site.register(Hardware)
admin.site.register(Option)
admin.site.register(Benchmark, BenchmarkAdmin)
admin.site.register(Comparison)

admin.site.register(Algorithm)
admin.site.register(RegisteredShortcut)
admin.site.register(ExtraValue)

#admin.site.register(OptionTool)
#admin.site.register(AlgorithmTool)
admin.site.register(OptionValue)