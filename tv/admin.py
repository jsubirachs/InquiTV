from django.contrib import admin
from myuser.models import MyUser
from myuser.admin import MyUserAdmin

from .models import UserAccessTV


class UserAccessTVInline(admin.StackedInline):
    model = UserAccessTV
    can_delete = False
    verbose_name_plural = 'User access tv'

class MyUserAdmin(MyUserAdmin):
    inlines = (UserAccessTVInline,)

#admin.site.unregister(User)    
admin.site.register(MyUser, MyUserAdmin)
