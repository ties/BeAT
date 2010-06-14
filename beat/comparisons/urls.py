from django.conf.urls.defaults import *
from beat.tools.feeds import LatestComparisons

#Let op: refereer je hiernaar, doe dat dan met {% url comparisons.views.naam %}. Dat views is nodig (...)
urlpatterns = patterns('beat.comparisons.views',
	# Form pages
	(r'^tool/$', 'compare_scatterplot'),
	(r'^model/$', 'compare_model'),
	
	# Show detail for a benchmark Comparison or ModelComparison, it takes the ID from the db
	url(r'^tool/(?P<id>\d+)/$', 'compare_detail', name="detail_benchmark"),
	url(r'^model/(?P<id>\d+)/$', 'compare_detail', {'model' : True},name="detail_model"),	
	
	# Graph image for the model-comparison
	(r'^tool/(?P<id>\d+)/scatterplot.png$', 'scatterplot'),
	(r'^model/(?P<id>\d+)/benchmark.png$', 'graph_model'),
	
	(r'^compareform/$', 'compareform'),

	# Exporting graphs
	url (r'^tool/(?P<id>\d+)/export$', 'export_graph',name="export_benchmark_graph"),
	url (r'^model/(?P<id>\d+)/export$', 'export_graph', {'model': True}, name="export_model_graph"),
	
	
	# RSS feed
	(r'^rss/$', LatestComparisons()),
	
	# Delete a benchmark Comparison or ModelComparison
	#! NEEDS AUTH
	url(r'^tool/(?P<id>\d+)/delete$', 'comparison_delete', name="delete_benchmark"),
	url(r'^model/(?P<id>\d+)/delete$', 'comparison_delete', {'model' : True}, name="delete_model"),
)

