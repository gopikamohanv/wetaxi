from django.shortcuts import *
from django.http import HttpResponse, Http404
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse

from wetaxi.main.forms import TaxiRegisterForm
from wetaxi.wetaxiconfigs.user_types import UserType
from wetaxi.wetaxiconfigs.email import send_email
from wetaxi.users.models import UserProfile
from wetaxi.static_items.models import Country, State, District, Circle
from wetaxi.taxi.models import TaxiProfile, TaxiBookingSchedule

from django.db.models import Q

import datetime

import json

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
	response.update({'states': State.objects.all()})
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

def register_user(request):
	response = {}
	response.update(csrf(request))

	if request.method == 'GET':
		return render_to_response('index.html', response)

	if request.method == 'POST':
		response.update({'taxi':get_object_or_404(TaxiProfile, pk=request.POST['taxiId'])})
		form = TaxiRegisterForm(request.POST)
		if form.is_valid():
			response.update({'form':form})

			try:
				user = User.objects.get(username=form.cleaned_data['email'])
			except:
				user = User(username=form.cleaned_data['email'], email=form.cleaned_data['email'])
				user.set_password(form.cleaned_data['password'])
				user.save()
				user_profile = UserProfile(user=user, user_type=UserType.types['Passenger'], phone=form.cleaned_data['mobile'])
				user_profile.save()
			else:
				response.update({'email_exists':True})
				return render_to_response('taxi_availability.html', response)	
			
			user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])	
			auth_login(request, user)
			return HttpResponseRedirect('/taxi/booking/confirm/'+ request.POST['taxiId'] +'/')	

		else:
			response.update({'form':form})
			response.update({'form_error':True})
			return render_to_response('taxi_availability.html', response)


def login(request):
	response = {}
	response.update(csrf(request))

	if request.method == 'GET':
		return HttpResponseRedirect('/')

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
			elif user_profile.user_type == UserType.types['Passenger']:
				if 'taxiId' in request.POST and request.POST['taxiId']:
					return HttpResponseRedirect('/taxi/booking/confirm/'+ request.POST['taxiId'] +'/')	
				return HttpResponse('passenger')
				return HttpResponseRedirect(reverse('passenger:dashboard')) 
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
	
	response.update({'states': State.objects.all()})

	user_profile = get_object_or_404(UserProfile, pk=pk)
	response.update({'user_profile': user_profile})
	response.update({'taxi_profiles': TaxiProfile.objects.filter(owner=user_profile)})
	return render_to_response('taxi_view.html', response)

def search_taxi(request):
	response = {}
	response.update(csrf(request))
	response.update({'states': State.objects.all()})

	if 'circle' in request.GET and request.GET['circle']:
		circle = request.GET['circle']
	else:
		raise Http404	

	circle_obj = get_object_or_404(Circle, pk=circle)
	response.update({'circle': circle_obj})
	response.update({'user_profiles': UserProfile.objects.filter(circle=circle_obj)})
	return render_to_response('taxi_list.html', response)	
	
def taxi_availability(request, pk):
	response = {}
	response.update(csrf(request))
	taxi = get_object_or_404(TaxiProfile, pk=pk)
	response.update({'taxi':taxi})
	if 'login_error' in request.GET and request.GET['login_error']:
		response.update({'login_error':True})
	return render_to_response('taxi_availability.html', response)	

def taxi_booking_confirm(request, pk):
	response = {}
	response.update(csrf(request))
	taxi = get_object_or_404(TaxiProfile, pk=pk)
	response.update({'taxi':taxi})
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/taxi/availability/'+ str(pk) + '/?login_error=1')
	
	response.update({'register_success':True})
	return render_to_response('taxi_availability.html', response)

def taxi_send_enquiry(request, pk):
	response = {}
	user = get_object_or_404(UserProfile, user=request.user)
	taxi = get_object_or_404(TaxiProfile, pk=pk)

	if 'fromDate' in request.POST and request.POST['fromDate']:
		from_date = request.POST['fromDate']
	else:
		raise Http404()

	if 'toDate' in request.POST and request.POST['toDate']:
		to_date = request.POST['toDate']
	else:
		raise Http404()

	person = request.POST['name']
	number = user.phone
	email = user.user.email
	route = request.POST['route']
	description = request.POST['description'] if 'description' in request.POST else 'Nil'

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

	if from_date < datetime.datetime.now():
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

	booked = TaxiBookingSchedule.objects.filter(Q(booking_from_date__range=(datetime.datetime.combine(from_date, datetime.datetime.min.time()), datetime.datetime.combine(from_date, datetime.datetime.max.time()))) | Q(booking_to_date__range=(datetime.datetime.combine(to_date, datetime.datetime.min.time()), datetime.datetime.combine(to_date, datetime.datetime.max.time()))) | Q(booking_from_date__lte=from_date, booking_to_date__gte=from_date), taxi=taxi, is_confirmed=True)

	if booked:
		return HttpResponse(
			json.dumps(
					{'status':False, 'message':'Error: This taxi is already booked for this date!!'}
			),
			content_type = 'application/json'
		)


	TaxiBookingSchedule.objects.create(taxi=taxi, booking_from_date=from_date, booking_to_date=to_date, contact_person=person, contact_number=number, route=route, booking_id=booking_id, is_enquiry=True, passenger=user)

	# SEND MAIL

	subject = 'Booking Enquiry'
	message = '<h3>You have a new Booking Enquiry</h3>'
	message += 'Name: ' + str(person) + '<br>'
	message += 'Email: ' + str(user.user.email) + '<br>'
	message += 'Mobile: ' + str(user.phone) + '<br>'
	message += 'Route: ' + str(route) + '<br>'
	message += 'Description: ' + str(description) + '<br>'
	message += 'From : ' + str(from_date) + '<br>'
	message += 'To : ' + str(to_date)
	send_email(subject, message, 'sureshvtt@gmail.com')	

	return HttpResponse(
		json.dumps(
				{'status':True, 'message':'Success: Enquiry Send Successfully. You will recieve an acknowledgement call within 45 minutes!!'}
		),
		content_type = 'application/json'
	)