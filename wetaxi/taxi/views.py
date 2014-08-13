from django.shortcuts import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.decorators import user_passes_test, login_required

from wetaxi.static_items.models import Country, State, District, Circle
from wetaxi.users.models import UserProfile
from wetaxi.wetaxiconfigs.user_types import UserType
from wetaxi.taxi.forms import TaxiAddForm, TaxiIconForm, TaxiRateForm, UpdateProfileForm
from wetaxi.taxi.models import * 

import os.path

def taxi_check(user):
	userprofile = get_object_or_404(UserProfile, user=user)
	return userprofile.user_type ==  UserType.types['Taxi']

@login_required
@user_passes_test(taxi_check)
def dashboard(request):
	response = {}
	response.update(csrf(request))

	userprofile = get_object_or_404(UserProfile, user=request.user)
	response.update({'taxi_list': TaxiProfile.objects.filter(owner=userprofile, is_valid=True)})
	return render_to_response('taxi_index.html', response)

@login_required
@user_passes_test(taxi_check)
def taxi_mylist(request):
	response = {}
	response.update(csrf(request))

	userprofile = get_object_or_404(UserProfile, user=request.user)
	response.update({'taxi_list': TaxiProfile.objects.filter(owner=userprofile, is_valid=True)})

	return render_to_response('taxi_mylist.html', response)

@login_required
@user_passes_test(taxi_check)
def taxi_new(request):
	response = {}
	response.update(csrf(request))
	response.update({'taxi_types': TaxiType.objects.all()})
	response.update({'states': State.objects.all()})

	if request.method == 'GET':
		return render_to_response('taxi_new.html', response)

	if request.method == 'POST':
		form = TaxiAddForm(request.POST)
		if form.is_valid():
			if 'user_type' in request.POST and request.POST['user_type']:
				user_type = request.POST['user_type']
				response.update({'user_type': user_type})
			else:
				return HttpResponseRedirect('/taxi/new/')

			userprofile = get_object_or_404(UserProfile, user=request.user)
			taxi_type = get_object_or_404(TaxiType, pk=form.cleaned_data['taxitype'])
			circle = get_object_or_404(Circle, pk=form.cleaned_data['circle'])

			taxi_profile = TaxiProfile(taxi_type=taxi_type, owner=userprofile, display_name=form.cleaned_data['name'], taxi_model=form.cleaned_data['model'], taxi_number=form.cleaned_data['taxinumber'], seat_capacity=form.cleaned_data['seats'],circle=circle,is_valid=True)
			taxi_profile.save()

			response.update({'success': True})
			return render_to_response('taxi_new.html', response)

		else:
			response.update({'form':form})
			response.update({'error':True})
			return render_to_response('taxi_new.html', response)


@login_required
@user_passes_test(taxi_check)
def taxi_features(request):
	response = {}
	response.update(csrf(request))

	if request.method == 'GET':
		return render_to_response('taxi_features.html', response)


@login_required
@user_passes_test(taxi_check)
def taxi_icon(request):
	response = {}
	response.update(csrf(request))
	response.update({'taxi_types': TaxiType.objects.all()})
	userprofile = get_object_or_404(UserProfile, user=request.user)
	response.update({'userprofile': userprofile})

	if request.method == 'GET':
		return render_to_response('taxi_icon.html', response)

	if request.method == 'POST':
		form = TaxiIconForm(request.POST, request.FILES)
		if form.is_valid():
			if 'user_type' in request.POST and request.POST['user_type']:
				user_type = request.POST['user_type']
				response.update({'user_type':user_type})
			else:
				return HttpResponseRedirect('/taxi/icon/')

			if 'taxi' in request.POST and request.POST['taxi']:
				taxi_number = request.POST['taxi']
			else:
				return HttpResponseRedirect('/taxi/icon/')

			if 'taxi_icon' in request.FILES and request.FILES['taxi_icon']:
				taxi_icon = request.FILES['taxi_icon']
			else:
				return HttpResponseRedirect('/taxi/icon/')
			basename, extension = os.path.splitext(taxi_icon.name)			
			filename =  os.path.abspath('wetaxi')+'/static/images/' + basename + extension
			destination = open(filename, 'wb+')
			for chunk in taxi_icon.chunks():
				destination.write(chunk)
			destination.close()	
			user_profile = get_object_or_404(UserProfile, user=request.user)
			try:
				taxi_profile = get_object_or_404(TaxiProfile, owner=user_profile, taxi_number=taxi_number)
				taxi_profile.icon_url = '/static/images/'+ basename + extension
				taxi_profile.save()
			except:
				return HttpResponse('You have added more than one taxi')	

		response.update({'success': True})
		return render_to_response('taxi_icon.html', response)

@login_required
@user_passes_test(taxi_check)
def taxi_remove(request):
	response = {}
	response.update(csrf(request))

	if 'id' in request.GET and request.GET['id']:
		taxi_id = request.GET['id']
	else:
		return render_to_response('taxi_mylist.html', response)	

	taxi_profile = get_object_or_404(TaxiProfile, pk=taxi_id)
	try:
		taxi_profile.delete()
	except:
		response.update({'cannot_delete':True})
		return render_to_response('taxi_mylist.html', response)
	response.update({'deleted':True})
	userprofile = get_object_or_404(UserProfile, user=request.user)
	response.update({'taxi_list': TaxiProfile.objects.filter(owner=userprofile, is_valid=True)})
	return render_to_response('taxi_mylist.html', response)	


@login_required
@user_passes_test(taxi_check)
def taxi_rate(request):
	response = {}
	response.update(csrf(request))
	response.update({'taxi_types': TaxiType.objects.all()})
	userprofile = get_object_or_404(UserProfile, user=request.user)
	response.update({'userprofile': userprofile})

	if request.method == 'GET':
		return render_to_response('taxi_rate.html', response)

	if request.method == 'POST':
		form = TaxiRateForm(request.POST)
		if form.is_valid():
			if 'user_type' in request.POST and request.POST['user_type']:
				user_type = request.POST['user_type']
				response.update({'user_type':user_type})
			else:
				return HttpResponseRedirect('/taxi/rate/')
			
			if 'taxitype' in request.POST and request.POST['taxitype']:
				taxitype = request.POST['taxitype']
			else:
				return HttpResponseRedirect('/taxi/rate/')


@login_required
@user_passes_test(taxi_check)
def update_profile(request):
	response = {}
	response.update(csrf(request))
	response.update({'states': State.objects.all()})
	user_profile = get_object_or_404(UserProfile, user=request.user)
	response.update({'user_profile':user_profile})

	if request.method == 'GET':
		return render_to_response('update_profile.html', response)

	if request.method == 'POST':
		form = UpdateProfileForm(request.POST)
		if form.is_valid():
			if 'user' in request.POST and request.POST['user']:
				user_pk = request.POST['user']
			else:
				return render_to_response('update_profile.html', response)
			
			user = get_object_or_404(User, pk=user_pk)
			district = get_object_or_404(District, pk=form.cleaned_data['district'])
			circle = get_object_or_404(Circle, pk=form.cleaned_data['circle'])
			try:
				user.first_name = form.cleaned_data['first_name']
				user.save()
				user_profile.address1 = form.cleaned_data['address'] 
				user_profile.district=district
				user_profile.circle=circle
				user_profile.save()
			except:
				response.update({'error':True})
				return render_to_response('update_profile.html', response)
			else:
				response.update({'success': True})
				return render_to_response('update_profile.html', response)	
		else:
			response.update({'error': True})
			return render_to_response('update_profile.html', response)

					

			

								


		







				

		
	
