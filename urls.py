from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


from django.conf import settings


urlpatterns = patterns('',
    # Example:
    # (r'^beat/', include('beat.foo.urls')),

	(r'^$', 'benchmarks.views.index'),
	(r'^tables/$', 'benchmarks.views.tables'),
	
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Auth pages
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	
	#static stuff
	
	(r'^tables/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
	(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
)
