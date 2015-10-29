from django.db import models
from django.conf import settings
#Para los signal:
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from constance.backends.database.models import Constance

class UserAccessTV(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile")
    buy_date = models.DateField(null=True, blank=True)
    free_access = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


#Signal para activar el profile en cada alta de usuario
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_useraccesstv_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = UserAccessTV(user=instance)
        profile.save()


#Signal para evitar el multilogueo
#No funciona con @receiver(user_logged_in, sender=settings.AUTH_USER_MODEL)
def register_user_to_cache(sender, user, request, **kwargs):
    registered = cache.get(user)
    if registered:
        previous_session_key = 'django.contrib.sessions.cache' + registered
        cache.delete(previous_session_key)
    cache.set(user, request.session.session_key)    
user_logged_in.connect(register_user_to_cache)


#Signal para borrar tv cache en el momento que cambie el acceso universal
@receiver(post_save, sender=Constance)
def delete_tv_cache(sender, created, instance, **kwargs):
    if cache.get('tv'):
        cache.delete('tv')
