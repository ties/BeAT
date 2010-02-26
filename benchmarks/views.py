from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import Context, loader
from django.shortcuts import render_to_response

from benchmarks.models import Option

COLUM_COUNT = 2

@login_required(redirect_field_name='next')
def index(request):
	list = Option.objects.all()
	count = list.count()
	list0 = list[:count/2+1] #alles voor de helft (excl)
	list1 = list[count/2+1:] #alles na de helft (incl)
	
	t = loader.get_template('base.html')
	c = Context({
		'pagetype': "Example page!",
		'lijstje0': list0,
		'lijstje1': list1,
		'size': count,
		'sidebar_content': "This is the side bar",
	})
	return HttpResponse(t.render(c));

def tables(request):
	t = loader.get_template('index_tables.html')
	c = Context({
		'username' : request.user.username,
	})
	return HttpResponse(t.render(c));	
	
#@login_required()
#def mudkip(request):
#	return render_to_response('index.html', {'username' : 'mudkip'})

#def index(request):
#	return HttpResponse('Hello world.')