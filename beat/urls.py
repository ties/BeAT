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
	(r'^test.png$', 'benchmarks.views.scatterplot'),
	(r'^benchmarks/$', 'benchmarks.views.benchmarks'),
	(r'^compare$', 'benchmarks.views.compare'),
	
	url(r'^compare/(?P<id>\d+)/$', 'benchmarks.views.compare_detail', name="detail_benchmark"),
	url(r'^compare/model/(?P<id>\d+)/$', 'benchmarks.views.compare_detail', {'model' : True},name="detail_model"),
	(r'^compare/model/(?P<id>\d+)/benchmark.png$', 'benchmarks.views.graph_model'),
	
	# User content
	(r'^user/compare/$', 'benchmarks.views.user_comparisons'),
	url(r'^user/compare/delete/(?P<id>\d+)/$', 'benchmarks.views.user_comparison_delete', name="delete_benchmark"),
	url(r'^user/compare/model/delete/(?P<id>\d+)/$', 'benchmarks.views.user_comparison_delete', {'model' : True}, name="delete_model"),
	
	# Comparisons
	(r'^compare/benchmark-(?P<id>\d+).png$', 'benchmarks.views.simple'),
	(r'^compare/model/$', 'benchmarks.views.compare_model'),

	# File upload
	(r'^upload/', 'benchmarks.views.upload_log'),
	
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Auth pages
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	
	# Graphs
)

# static media: DEVELOPMENT ONLY!
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
    (r'^site_media/(?P<path>.*)$', 
        'serve', {
        'document_root': os.path.join(settings.SITE_ROOT, 'site_media'),
        'show_indexes': True }),)
