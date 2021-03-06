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

class TaxiRate(models.Model):
	taxi = models.ForeignKey(TaxiProfile)
	rate = models.CharField(max_length=100, null=True, blank=True)
	with_ac = models.CharField(max_length=255, null=True, blank=True)

class TaxiGellery(models.Model):
	taxi = models.ForeignKey(TaxiProfile)
	image_url = models.URLField(max_length=255)	


		

