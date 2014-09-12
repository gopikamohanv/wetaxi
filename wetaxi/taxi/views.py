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
import json
import datetime
import time
from datetime import timedelta

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.db.models import Q

key = 'AKIAJ4BESZTCA2ITP7BA'
secretkey = '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'

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
				uploaded_file = request.FILES['taxi_icon']
			else:
				return HttpResponseRedirect('/taxi/icon/')

			basename, extension = os.path.splitext(uploaded_file.name)
			ext = extension.lower()
			if not ext == '.png' and not ext == '.jpg' and not ext == '.jpeg':
				response.update({'image_type_error':True}) 
				return render_to_response('taxi_icon.html', response)

			new_name = str(datetime.datetime.now().strftime("%b%d%Y%H%M%S"))
			filename = new_name
			key_name = filename + extension     # For use with Amazon
			filename = '/tmp/' + filename + extension
			destination = open(filename, 'wb+')
			for chunk in uploaded_file.chunks():
				destination.write(chunk)
			destination.close()
			size = os.path.getsize(filename)
			size = float((size / 1024) / 1024)
			if size > 2:
				response.update({'image_size_error':True}) 
				return render_to_response('taxi_icon.html', response)

			#Write the file to Amazon and generate the link
			try:
				conn = S3Connection(key, secretkey) # DO NOT LOOSE THIS KEY!!!!!
				bucket = conn.get_bucket('uploads.wetaxi.in')
				k = Key(bucket)
				k.key = key_name
				k.set_contents_from_filename(filename)
				k.set_acl('public-read')
			except:
				return HttpResponse('One of our servers has encountered an error and needs to close. We are sorry for your inconvenience. Please try agin later')
			else:
				img_url = 'http://uploads.wetaxi.in.s3.amazonaws.com/' + key_name

			user_profile = get_object_or_404(UserProfile, user=request.user)
			try:
				taxi_profile = get_object_or_404(TaxiProfile, owner=user_profile, taxi_number=taxi_number)
				taxi_profile.icon_url = img_url
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
			
			if 'taxi' in request.POST and request.POST['taxi']:
				taxi = request.POST['taxi']
			else:
				return HttpResponseRedirect('/taxi/rate/')

			if 'taxi_rate' in request.POST and request.POST['taxi_rate']:
				taxi_rate = request.POST['taxi_rate']
			else:
				return HttpResponseRedirect('/taxi/rate/')

			taxi_obj = get_object_or_404(TaxiProfile, taxi_number=taxi)
			try:
				rate = TaxiRate()
				rate.taxi = taxi_obj
				rate.rate = taxi_rate
				rate.save()	
			except:
				raise Http404
			else:
				response.update({'success':True})
				return render_to_response('taxi_rate.html', response)		

		else:
			response.update({'error':True})
			return render_to_response('taxi_rate.html', response)

@login_required
@user_passes_test(taxi_check)
def taxi_rate_view(request):
	response = {}
	user_profile = get_object_or_404(UserProfile, user=request.user)
	response.update({'taxis':TaxiProfile.objects.filter(owner=user_profile)})
	return render_to_response('taxi_rate_view.html', response)


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

					
@login_required
@user_passes_test(taxi_check)
def booking_schedule(request):
	response = {}
	response.update(csrf(request))
	user_profile = get_object_or_404(UserProfile, user=request.user)
	response.update({'user_profile':user_profile})
	response.update({'taxi_types':TaxiType.objects.all()})
	response.update({'passengers':UserProfile.objects.filter(user_type=UserType.types['Passenger'])})

	taxis = TaxiProfile.objects.filter(owner=user_profile)
	if 'type' in request.GET and request.GET['type']:
		taxi_type_id = request.GET['type']
		taxi_type = get_object_or_404(TaxiType, id=taxi_type_id)
		taxis = TaxiProfile.objects.filter(owner=user_profile, taxi_type=taxi_type)

	response.update({'taxis':taxis})
	return render_to_response('taxi_booking_schedule.html', response)

@login_required
@user_passes_test(taxi_check)
def taxi_schedule_events(request):
	result = {}
	result['success'] = '1'
	result['result'] = []

	from_date = int(request.GET['from'])
	to_date = int(request.GET['to'])

	from_date = datetime.datetime.fromtimestamp(from_date/1000.0)
	to_date = datetime.datetime.fromtimestamp(to_date/1000.0)

	taxi = None
	if 'taxi' in request.GET and request.GET['taxi']:
		taxi_id = request.GET['taxi']
		try:
			taxi = TaxiProfile.objects.get(id=taxi_id)
		except:
			pass
	else:
		pass

	while from_date <= to_date:
		x = {}
		x['start'] = int(time.mktime((from_date - timedelta(days=1)).timetuple()) * 1000)
		x['end'] = int(time.mktime((from_date - timedelta(days=1)).timetuple()) * 1000)
		booked = TaxiBookingSchedule.objects.filter(Q(booking_from_date__range=(datetime.datetime.combine(from_date, datetime.datetime.min.time()), datetime.datetime.combine(from_date, datetime.datetime.max.time()))) | Q(booking_to_date__range=(datetime.datetime.combine(from_date, datetime.datetime.min.time()), datetime.datetime.combine(from_date, datetime.datetime.max.time()))) | Q(booking_from_date__lte=from_date, booking_to_date__gte=from_date), taxi=taxi)
		if booked:
			x['title'] = 'Booked (' + str(datetime.datetime.strftime(booked[0].booking_from_date, '%d %b %I:%M %p')) + ' to ' + str(datetime.datetime.strftime(booked[0].booking_to_date, '%d %b %I:%M %p')) + ')'
			x['class'] = 'event-important'
		elif from_date < datetime.datetime.today():
			from_date = from_date + timedelta(days=1)
			continue
		else:
			x['title'] = 'Booking Available'
			x['class'] = 'event-success'
			x['url'] = 'javascript:hello(\'' + str(from_date.strftime('%m/%d/%Y')) + ' 10:00 AM \')'
		result['result'].append(x)

		from_date = from_date + timedelta(days=1)


	return HttpResponse(
		json.dumps(
				result
		),
		content_type = 'application/json'
	)

@login_required
@user_passes_test(taxi_check)
def taxi_booking(request, pk):
	response = {}
	taxi = get_object_or_404(TaxiProfile, pk=pk)

	if 'from' in request.POST and request.POST['from']:
		from_date = request.POST['from']
	else:
		raise Http404()

	if 'to' in request.POST and request.POST['to']:
		to_date = request.POST['to']
	else:
		raise Http404()

	person = request.POST['person']
	number = request.POST['number']
	address = request.POST['address']
	route = request.POST['route']

	from_date = from_date.split(' ')
	from_date = str(from_date[0]) + ' ' + str(from_date[1]) + ' ' + str(from_date[2])
	from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y %I:%M %p')

	to_date = to_date.split(' ')
	to_date = str(to_date[0]) + ' ' + str(to_date[1]) + ' ' + str(to_date[2])
	to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y %I:%M %p')

	if to_date < from_date:
		return HttpResponse(
			json.dumps(
					{'status':False, 'message':'Error: End Date cannot be less than Start Date !!'}
			),
			content_type = 'application/json'
		)

	if from_date < datetime.datetime.today():
		return HttpResponse(
			json.dumps(
					{'status':False, 'message':'Error: No Booking !!'}
			),
			content_type = 'application/json'
		)

	booking_id = 1000
	latest_booking_id = TaxiBookingSchedule.objects.all().order_by('-id')
	if latest_booking_id:
		booking_id = int(latest_booking_id[0].booking_id) + 1

	booked = TaxiBookingSchedule.objects.filter(Q(booking_from_date__range=(datetime.datetime.combine(from_date, datetime.datetime.min.time()), datetime.datetime.combine(from_date, datetime.datetime.max.time()))) | Q(booking_to_date__range=(datetime.datetime.combine(to_date, datetime.datetime.min.time()), datetime.datetime.combine(to_date, datetime.datetime.max.time()))) | Q(booking_from_date__lte=from_date, booking_to_date__gte=from_date), taxi=taxi)

	if booked:
		return HttpResponse(
			json.dumps(
					{'status':False, 'message':'Error: This taxi is already booked for this date!!'}
			),
			content_type = 'application/json'
		)


	TaxiBookingSchedule.objects.create(taxi=taxi, booking_from_date=from_date, booking_to_date=to_date, contact_person=person, contact_number=number, contact_address=address, route=route, booking_id=booking_id)
	return HttpResponse(
		json.dumps(
				{'status':True, 'message':'Success: Booking Completed Successfully!!'}
		),
		content_type = 'application/json'
	)






		







				

		
	
