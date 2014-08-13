from django import forms

class TaxiAddForm(forms.Form):
	taxitype = forms.CharField(max_length=32)
	name = forms.CharField(max_length=255)
	model = forms.CharField(max_length=255)
	taxinumber = forms.CharField(max_length=255)
	seats = forms.CharField(max_length=255)
	state =  forms.CharField(max_length=255)
	district = forms.CharField(max_length=255)
	circle = forms.CharField(max_length=255)


class TaxiIconForm(forms.Form):
	taxitype = forms.CharField(max_length=32)
	taxi = forms.CharField(max_length=32)
	taxi_icon = forms.FileField()	

class TaxiRateForm(forms.Form):
	taxitype = forms.CharField(max_length=20)
	taxi = forms.CharField(max_length=20)
	taxi_rate = forms.CharField(max_length=20)

class UpdateProfileForm(forms.Form):
	first_name = forms.CharField(max_length=255)	
	address = forms.CharField(max_length=1024)
	state = forms.CharField(max_length=20)
	district = forms.CharField(max_length=20)
	circle = forms.CharField(max_length=20)

		