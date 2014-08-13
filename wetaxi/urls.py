from django.conf.urls import patterns, include, url
from django.contrib import admin

from main import views
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wetaxi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
	url(r'^register/taxi/', views.register_taxi, name='register_taxi'),
    url(r'^taxi/view/(?P<pk>\w+)/$', views.taxi_view, name='taxi_view'),

	# Views of taxi app
	url(r'^taxi/', include('wetaxi.taxi.urls', namespace='taxi')),

    # Ajax views
    url(r'^ajax/district/', views.ajax_district, name='ajax_district'),
    url(r'^ajax/circle/', views.ajax_circle, name='ajax_circle'),
    url(r'^ajax/taxi/', views.ajax_taxi, name='ajax_taxi'),
)
