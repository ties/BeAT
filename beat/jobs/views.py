from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse

from beat.jobs.forms import *

"""Page for batch job generation
"""
@login_required
def jobgen(request):
	#fetch tool/algorithms
	#t = Tool.objects.all()
	#a = Algorithm.objects.all()
	#fetch models
	#m = Model.objects.all()
	#display page
	jobform = JobGenForm()
	suiteform = SuiteGenForm()
	return render_to_response('jobs/jobgen.html', {'jform':jobform, 'sform':suiteform}, context_instance=RequestContext(request))

"""Generate batch job
"""
@login_required
def jobgen_create(request):
	if request.method == 'POST': # If the form has been submitted...	
		form = JobGenForm(request.POST) # A form bound to the POST data
		if (form.is_valid()):
			# Process the data in form.cleaned_data
			t = form.cleaned_data['tool']
			a = form.cleaned_data['algorithm']
			m = form.cleaned_data['models']
			import beat.jobs.jobs
			j = beat.jobs.jobs.JobGenerator()
			jobs = []
			for x in m:
				jobs.append(j.pbsgen("1", "%s%s"%(t.name,a.name),"--cache","%s"%(x.name)))
			return render_to_response('jobs/jobgen_create.html', { 'job':jobs }, context_instance=RequestContext(request))
		else:
			return redirect('jobgen')
	else:
		return redirect('jobgen')

"""Generate batch job suite
"""
@login_required
def suitegen_create(request):
	if request.method == 'POST': # If the form has been submitted...
		form = JobGenForm(request.POST) # A form bound to the POST data
		if (form.is_valid()):
			# Process the data in form.cleaned_data
			models = form.cleaned_data['models']
			import beat.jobs.jobs
			import beat.jobs.jobs_fileserv
			j = beat.jobs.jobs.JobGenerator()
			for model in models:
				j.suitegen(model.name)
			filename, file = beat.jobs.jobs_fileserv.to_tar(j.jobs)
			response = HttpResponse(mimetype='application/x-gzip')
			response['Content-Disposition'] = 'attachment; filename=%s' % filename
			file.seek(0)	# Just making sure...
			response.write(file.read())
			response.flush()
			return response
		else:
			return redirect('jobgen')
	else:
		return redirect('jobgen')
