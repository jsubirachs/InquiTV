from django.conf.urls import include, url
from . import views


urlpatterns = [
    #url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'post_change_redirect': 'index'}, name='password_change'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^contact/login/$', views.contact_login, name='contact_login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        views.signup_confirm,
        name="signup_confirm"),
    url(r'^captcha/', include('captcha.urls')),

    url(r'^password/reset/$', 
        'django.contrib.auth.views.password_reset', 
        name="password_reset"),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name="password_reset_done"),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm', 
        name="password_reset_confirm"),
    url(r'^password/done/$', 
        'django.contrib.auth.views.password_reset_complete',
        name="password_reset_complete"),
    url(r'^email/change/$', views.email_change, name='email_change'),
    url(r'^delete/account/$', views.delete_account, name='delete_account'),
]
