from beat.benchmarks.models import *
from django.contrib import admin

class HardwareInline(admin.TabularInline):
	model = BenchmarkHardware
	extra = 1
	
class OptionInline(admin.TabularInline):
	model = BenchmarkOption
	extra = 1

class BenchmarkAdmin(admin.ModelAdmin):
	list_display = ('model_ID', 'tool_ID')
	list_filter = ['date_time']
	search_fields = ['model_ID__name', 'tool_ID__name']
	fieldsets = [
		('Configuration', {'fields': ['model_ID','tool_ID']}),
		('Date information', {'fields': ['date_time']}),
		('Output data', {'fields': ['run_time','transition_count','states_count','memory_used']}),
	]
	inlines = [HardwareInline, OptionInline]
	
admin.site.register(Model)
admin.site.register(Tool)
admin.site.register(Hardware)
admin.site.register(Option)
admin.site.register(Benchmark, BenchmarkAdmin)

