from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
import wetaxi.taxi.views

urlpatterns = patterns('',
	url(r'^dashboard/$', wetaxi.taxi.views.dashboard, name='dashboard'),
	url(r'^update/profile/$', wetaxi.taxi.views.update_profile, name='update_profile'),
	url(r'^mylist/$', wetaxi.taxi.views.taxi_mylist, name='taxi_mylist'),
	url(r'^new/$', wetaxi.taxi.views.taxi_new, name='taxi_new'),
	url(r'^features/$', wetaxi.taxi.views.taxi_features, name='taxi_features'),
	url(r'^icon/$', wetaxi.taxi.views.taxi_icon, name='taxi_icon'),
	url(r'^remove/$', wetaxi.taxi.views.taxi_remove, name='taxi_remove'),
	url(r'^rate/$', wetaxi.taxi.views.taxi_rate, name='taxi_rate'),
	url(r'^booking/schedule/$', wetaxi.taxi.views.booking_schedule, name='booking_schedule'),
	url(r'^schedule/events/$', wetaxi.taxi.views.taxi_schedule_events, name='taxi_schedule_events'),
	url(r'^booking/(?P<pk>\w+)/$', wetaxi.taxi.views.taxi_booking, name='taxi_booking'),
)