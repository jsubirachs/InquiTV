from functools import wraps
from django.http import Http404


#Decorator for protect admin from intruders
def staff_or_404(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, raising a 404 if necessary.
    """
    @wraps(view_func)
    def new_view_func(request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_admin:
                # The user is valid. Continue to the admin page.
                return view_func(request, *args, **kwargs)

        raise Http404
    return new_view_func
