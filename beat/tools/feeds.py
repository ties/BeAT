from django.contrib.syndication.views import Feed
from beat.comparisons.models import ModelComparison, Comparison

class LatestComparisons(Feed):
	title = "Benchmark Analysis Toolkit"
	link = "/comparisons/"
	description = "New comparisons are shown here."

	def items(self):
		return ModelComparison.objects.order_by('-date_time')[:5]

	def item_title(self, item):
		return item.name

	def item_description(self, item):
		return str(item.algorithm) + ' ' + str(item.tool)
