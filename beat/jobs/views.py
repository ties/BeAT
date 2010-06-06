from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
import re

from beat.jobs.forms import *

@login_required
def jobgen_load(request):
	match = re.search(r'/id=(?P<id>[0-9]+)', request.path)
	id = match.group('id')
	if not id:
		return HttpResponseBadRequest()
	id = int(id)
	jfilter = get_object_or_404(JobsFilter, pk=id, user=request.user)
	jobform = JobGenForm()
	jobform.change_defaults(jfilter)
	suiteform = SuiteGenForm()
	return render_to_response('jobs/jobgen.html', {'jform':jobform, 'sform':suiteform}, context_instance=RequestContext(request))

"""Page for batch job generation
"""
@login_required
def jobgen(request):
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
			o = form.cleaned_data['options']
			if (form.name):
				c, created = JobsFilter.objects.get_or_create(
					name = name,
					user = request.user,
					tool = t,
					algorithm = a,
					model = m,
					options = o
				)
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


@login_required()
def user_jobs(request):
	jobs = (JobsFilter.objects.filter(user=request.user))
	return render_to_response('jobs/user_jobs.html', { 'user_jobs' : jobs }, context_instance=RequestContext(request) )
	
	
