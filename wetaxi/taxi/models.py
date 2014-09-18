from django.db import models
from django.contrib.auth.models import User

from wetaxi.users.models import UserProfile
from wetaxi.static_items.models import Circle

class TaxiType(models.Model):
	taxi_type = models.CharField(max_length=100)

class TaxiProfile(models.Model):
	taxi_type = models.ForeignKey(TaxiType)
	owner = models.ForeignKey(UserProfile)
	display_name = models.CharField(max_length=255, null=True, blank=True)
	taxi_model = models.CharField(max_length=255, null=True, blank=True)
	taxi_number = models.CharField(max_length=255, null=True, blank=True)
	seat_capacity = models.CharField(max_length=32, null=True, blank=True)
	icon_url = models.URLField(max_length=225, null=True, blank=True)
	circle = models.ForeignKey(Circle)
	is_valid = models.NullBooleanField(default=None)
	feature = models.TextField()
	date_registered = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.display_name) 

	def get_rate(self):
		try:
			taxi_rate = TaxiRate.objects.get(taxi=self)
			return taxi_rate.rate
		except:
			return None	

class TaxiRate(models.Model):
	taxi = models.ForeignKey(TaxiProfile)
	rate = models.CharField(max_length=100, null=True, blank=True)
	with_ac = models.CharField(max_length=255, null=True, blank=True)

class TaxiGellery(models.Model):
	taxi = models.ForeignKey(TaxiProfile)
	image_url = models.URLField(max_length=255)	

class DriverProfile(models.Model):
	name = models.CharField(max_length=255)
	address = models.TextField()
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=20,null=True, blank=True)
	mobile = models.CharField(max_length=20,null=True, blank=True)
	added_by = models.ForeignKey(UserProfile)

	def __unicode__(self):
		return self.name

class TaxiBookingSchedule(models.Model):
	taxi = models.ForeignKey(TaxiProfile)
	booking_from_date = models.DateTimeField()
	booking_to_date = models.DateTimeField()
	route = models.TextField()
	contact_person = models.TextField()
	contact_number = models.CharField(max_length=255)
	contact_address = models.TextField() 
	booking_id = models.SlugField(db_index=True, unique=True)
	is_enquiry = models.BooleanField(default=False)
	is_confirmed = models.BooleanField(default=False)
	description = models.TextField(blank=True)
	passenger = models.ForeignKey(UserProfile, null=True, blank=True)

	def __unicode__(self):
		return str(self.taxi) + ' - ' + 	str(self.booking_from_date.date()) + '---' + str(self.booking_to_date.date()) + ')'




		

