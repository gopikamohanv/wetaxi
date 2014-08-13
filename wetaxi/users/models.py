from django.db import models
from django.contrib.auth.models import User

from wetaxi.static_items.models import *


# User type & User profile 
class UserProfile(models.Model):
	user = models.ForeignKey(User)
	gender = models.CharField(max_length=2, null=True, blank=True)
	dob = models.DateField(null=True, blank=True)
	address1 = models.TextField(null=True, blank=True)
	address2 = models.TextField(null=True, blank=True)
	district = models.ForeignKey(District, null=True, blank=True)
	circle = models.ForeignKey(Circle,null=True, blank=True)
	pincode = models.CharField(max_length=10,null=True, blank=True)
	phone = models.CharField(max_length=20,null=True, blank=True)
	user_type = models.CharField(max_length=2, blank=True)
	added_by = models.CharField(max_length=50,null=True, blank=True)
	plain_password = models.CharField(max_length=50,null=True, blank=True)
	profile_pic = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return self.user.username
