from django import forms

class TaxiRegisterForm(forms.Form):
	email = forms.CharField(max_length=255)
	password = forms.CharField(max_length=32)
	mobile = forms.CharField(min_length=10, max_length=10)