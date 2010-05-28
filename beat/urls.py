from django.conf.urls.defaults import *
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^beat/', include('beat.foo.urls')),
	(r'^benchmarks/ajax/', include('beat.benchmarks.ajax_urls')),
	(r'^$', 'benchmarks.views.index'),
	(r'^benchmarks/export/$', 'benchmarks.views.export_benchmarks'),
	
	# Graph for benchmark-scatterplot, this needs to be implemented in views.benchmarks
	(r'^benchmarks/$', 'benchmarks.views.benchmarks'),
	(r'^test.png$', 'comparisons.views.scatterplot'),
	url (r'^export/(?P<id>\d+)$', 'comparisons.views.export_graph',name="export_benchmark_graph"),
	url (r'^export/model/(?P<id>\d+)$', 'comparisons.views.export_graph', {'model': True}, name="export_model_graph"),
	
	# Show detail for a benchmark Comparison or ModelComparison, it takes the ID from the db
	url(r'^compare/(?P<id>\d+)/$', 'comparisons.views.compare_detail', name="detail_benchmark"),
	url(r'^compare/model/(?P<id>\d+)/$', 'comparisons.views.compare_detail', {'model' : True},name="detail_model"),
	# Graph for the model-comparison
	(r'^compare/model/(?P<id>\d+)/benchmark.png$', 'comparisons.views.graph_model'),
	
	(r'^compare/benchmarks/$', 'comparisons.views.compare_scatterplot'),
	(r'^compare/(?P<id>\d+)/scatterplot.png$', 'comparisons.views.scatterplot'),
	
	# View saved comparisons
	(r'^user/compare/$', 'benchmarks.views.user_comparisons'),
	# Delete a benchmark Comparison or ModelComparison
	#! NEEDS AUTH
	url(r'^user/compare/delete/(?P<id>\d+)/$', 'benchmarks.views.user_comparison_delete', name="delete_benchmark"),
	url(r'^user/compare/model/delete/(?P<id>\d+)/$', 'benchmarks.views.user_comparison_delete', {'model' : True}, name="delete_model"),
	
	# Old Benchmark compare graph, produces histogram
	(r'^compare/benchmark-(?P<id>\d+).png$', 'comparisons.views.simple'),
	# Form with filters for ModelComparisons
	(r'^compare/model/$', 'comparisons.views.compare_model'),

	#Job Generation
	#authorization should be here too
	(r'^jobgen/$', 'jobs.views.jobgen'),
	(r'^jobgen/go/$', 'jobs.views.jobgen_create'),
	(r'^suitegen/go/$', 'jobs.views.suitegen_create'),
	
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Auth pages
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	
	# Overige pagina's
	(r'^colophon/$', 'benchmarks.views.colophon'),
)

# static media: DEVELOPMENT ONLY!
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
    (r'^site_media/(?P<path>.*)$', 
        'serve', {
        'document_root': os.path.join(settings.SITE_ROOT, 'site_media'),
        'show_indexes': True }),)
