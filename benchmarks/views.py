from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import Context, loader
from django.shortcuts import render_to_response

# @login_required(redirect_field_name='next')
# def index(request):
#	t = loader.get_template('index.html')
#	c = Context({
#		'username' : request.user.username,
#	})
#	return HttpResponse(t.render(c));

#@login_required()
#def mudkip(request):
#	return render_to_response('index.html', {'username' : 'mudkip'})

def index(request):
	return HttpResponse('Hello world.')