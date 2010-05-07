import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext, loader
from django.db.models.loading import get_model

def export(qs, title="QuerySet"):
	model = qs.model
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s.csv' % title
	writer = csv.writer(response)
	# Write headers to CSV file
	headers = []
	for field in model._meta.fields:
		headers.append(field.name)
	writer.writerow(headers)
	# Write data to CSV file
	for obj in qs:
		row = []
		for field in headers:
			if field in headers:
				val = getattr(obj, field)
				if callable(val):
					val = val()
				row.append(val)
		writer.writerow(row)
	# Return CSV file to browser as download
	return response
