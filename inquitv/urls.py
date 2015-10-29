from django.conf.urls import include, url
from django.contrib import admin

#Add decorator to admin for protect from intruders
from decorator_include import decorator_include
from .decorators import staff_or_404


urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', decorator_include(staff_or_404, admin.site.urls)),
    url(r'', include('tv.urls')),
]
