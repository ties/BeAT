from beat.benchmarks.models import *
from django.contrib import admin

class HardwareInline(admin.TabularInline):
	model = BenchmarkHardware
	extra = 1
	
class OptionInline(admin.TabularInline):
	model = BenchmarkOption
	extra = 1

class BenchmarkAdmin(admin.ModelAdmin):
	list_display = ('model', 'tool', 'date_time', 'finished','user_time', 'system_time', 'elapsed_time', 'memory_VSIZE', 'memory_RSS', 'states_count', 'transition_count')
	list_filter = ['date_time']
	search_fields = ['model__name', 'tool__name']
	fieldsets = [
		('Configuration', {'fields': ['model','tool','finished']}),
		('Date information', {'fields': ['date_time']}),
		('Output data', {'fields': ['user_time', 'system_time', 'elapsed_time','transition_count','states_count','memory_VSIZE', 'memory_RSS']}),
	]
	inlines = [HardwareInline, OptionInline]
	
admin.site.register(Model)
admin.site.register(Tool)
admin.site.register(Parser)
admin.site.register(Hardware)
admin.site.register(Option)
admin.site.register(Benchmark, BenchmarkAdmin)
admin.site.register(Comparison)
