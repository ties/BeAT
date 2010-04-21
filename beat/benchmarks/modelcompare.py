import json
def ajaxmodels(request):
	print request.POST.lists()
	dump = json.dumps({'id':1})
	print dump
	return HttpResponse(dump,mimetype="application/json")