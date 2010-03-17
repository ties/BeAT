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
	(r'^tables/$', 'benchmarks.views.tables'),
	(r'^benchmarks/$', 'benchmarks.views.benchmarks'),
	(r'^compare/$', 'benchmarks.views.compare_post'),
	(r'^compare/(?P<id>(\d+(\+\d)*))/$', 'benchmarks.views.compare'),
	(r'^compare/(?P<id>(\d+(\+\d)*))/benchmark.png$', 'benchmarks.views.simple'),
	(r'^compare/model/$', 'benchmarks.views.compare_model'),
	(r'^compare/model/benchmark.png$', 'benchmarks.views.graph_model'),

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
