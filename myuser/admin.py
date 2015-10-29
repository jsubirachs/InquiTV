from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import flatten_fieldsets

from .models import MyUser
from .forms import UserCreationForm, UserChangeForm

class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'is_active', 'is_admin', 'date_joined',
                    'last_login', 'buy_date', 'free_access')
    list_filter = ('is_superuser', 'is_active', 'is_admin', 'date_joined', 'last_login', 'profile__buy_date', 'profile__free_access')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'date_joined', 'last_login',
                           'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser')}),
    )

    #Para meter free_access en el list_display
    def free_access(self, obj):
        try:
            free_access = obj.profile.free_access
            return free_access
        except:
            return ""
    free_access.short_description = 'Free Access'

    #Para meter buy_date en el list_display
    def buy_date(self, obj):
        try:
            buy_date = obj.profile.buy_date
            return buy_date
        except:
            return ""
    buy_date.short_description = 'Buy Date'

    #Alteramos un campo a solo lectura para los no superusuarios y que no tengan acceso a configuraciones delicadas del admin.
    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if not request.user.is_superuser:
                if request.user.username == obj.username or not obj.is_admin:
                    return self.readonly_fields + ('is_superuser',)
                else:
                    return self.readonly_fields + tuple(flatten_fieldsets(self.get_fieldsets(request, obj)))
        return self.readonly_fields
    
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}),
    )
    
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ()

# Now register the new UserAdmin...
#admin.site.register(MyUser, MyUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
