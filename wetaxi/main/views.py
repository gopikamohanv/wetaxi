from django.shortcuts import *
from django.http import HttpResponse, Http404
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse

from wetaxi.main.forms import TaxiRegisterForm
from wetaxi.wetaxiconfigs.user_types import UserType
from wetaxi.users.models import UserProfile
from wetaxi.static_items.models import Country, State, District, Circle
from wetaxi.taxi.models import TaxiProfile

#Ajax views
def ajax_district(request):
	response = {}
	if 'state' in request.GET and request.GET['state']:
		state = request.GET['state']
	else:
		raise Http404

	state_obj = get_object_or_404(State, pk=state)
	response.update({'districts': District.objects.filter(state=state_obj)})
	return render_to_response('ajax_districts.html', response)

def ajax_circle(request):
	response = {}
	if 'district' in request.GET and request.GET['district']:
		district = request.GET['district']
	else:
		raise Http404
	district_obj = get_object_or_404(District, pk=district)
	response.update({'circles': Circle.objects.filter(district=district_obj)})
	return render_to_response('ajax_circles.html', response)		

def ajax_taxi(request):
	response = {}
	if 'taxitype' in request.GET and request.GET['taxitype']:
		taxitype = request.GET['taxitype']
	else:
		raise Http404
	
	if 'user' in request.GET and request.GET['user']:
		user = request.GET['user']
	else:
		raise Http404
	user_obj = get_object_or_404(UserProfile, pk=user)
	response.update({'taxi_list': TaxiProfile.objects.filter(taxi_type=taxitype, owner=user_obj)})
	return render_to_response('ajax_taxi.html', response)

#Index view for main page ---Created by Viru---
def index(request):
	response = {}
	response.update(csrf(request))
	response.update({'user_profiles': UserProfile.objects.filter(user_type='1').order_by('-pk')[:10]})
	return render_to_response('index.html', response)

def register_taxi(request):
	response = {}
	response.update(csrf(request))

	if request.method == 'GET':
		return render_to_response('index.html', response)

	if request.method == 'POST':
		form = TaxiRegisterForm(request.POST)
		if form.is_valid():
			response.update({'form':form})

			if 'user_type' in request.POST and request.POST['user_type']:
				user_type = request.POST['user_type']
				response.update({'user_type':user_type})
			else:
				response.update({'error':True})
				return render_to_response('index.html', response)

			try:
				user = User.objects.get(username=form.cleaned_data['email'])
			except:
				user = User(username=form.cleaned_data['email'], email=form.cleaned_data['email'])
				user.set_password(form.cleaned_data['password'])
				user.save()
				user_profile = UserProfile(user=user, user_type=user_type, phone=form.cleaned_data['mobile'])
				user_profile.save()
			else:
				response.update({'user_exists':True})
				return render_to_response('index.html', response)	
			
			if user_type == UserType.types['Taxi']:
				return render_to_response('taxi_dashboard.html', response)
			else:
				return render_to_response('passenger_dashboard.html', response)	

		else:
			response.update({'form':form})
			response.update({'form_error':True})
			return render_to_response('index.html', response)


def login(request):
	response = {}
	response.update(csrf(request))

	if request.method == 'GET':
		return render_to_response('index.html', response)

	if request.method == 'POST':
		username = request.POST.get('email','')
		password = request.POST.get('password', '')
		user = authenticate(username=username, password=password)	
		if user is not None:
			auth_login(request, user)
			try:
				user_profile = UserProfile.objects.get(user=user)
			except:
				return HttpResponse('UserProfile Not Found!')

			if user_profile.user_type == UserType.types['Taxi']:
				return HttpResponseRedirect(reverse('taxi:dashboard')) 		
		else:
			response.update({'invalid_user': True})
			return render_to_response('index.html', response)

def logout(request):
	response = {}
	response.update(csrf(request))

	auth_logout(request)
	return HttpResponseRedirect('/')	


def taxi_view(request,pk):
	response = {}
	response.update(csrf(request))

	user_profile = get_object_or_404(UserProfile, pk=pk)
	response.update({'user_profile': user_profile})
	response.update({'taxi_profiles': TaxiProfile.objects.filter(owner=user_profile)})
	return render_to_response('taxi_view.html', response)
	
				


