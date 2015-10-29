from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tv/$', views.tv, name='tv' ),
    url(r'^live/', views.live, name='live' ),
    url(r'^subscription/$', views.subscription, name='subscription' ),
    url(r'', include('myuser.urls')),
]
