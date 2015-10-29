from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
#from django.contrib.auth.forms import UserCreationForm
from .forms import (UserCreationCaptchaForm, ChangeEmailForm,
                          DeleteAccountForm, ContactLoginForm, ContactForm)
from .token import signup_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template import loader
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.conf import settings


def my_send_mail(subject_template_name, email_template_name,
                  context, from_email, to_email):        
        """
        Sends a django.core.mail.send_mail to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        try:
                return send_mail(subject, body, from_email, [to_email],
                            fail_silently=False)
        except Exception as error:
                return error


@csrf_protect
def signup(request):
    token_generator = signup_token_generator
    if request.method == 'POST':
        form = UserCreationCaptchaForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            # Enviar email con el link de activacion,
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            }
            
            opts = {
                'subject_template_name': 'registration/signup_subject.txt',
                'email_template_name': 'registration/signup_email.html',
                'context': context,
                'from_email': None,
                'to_email': user.email,
                }
            sended = my_send_mail(**opts)
            if sended != 1:
                    # si el email de activacion falla, borrar usuario
                    user.delete()
                    return render(request,
                                  'registration/registration_complete.html',
                                  {'form':form, 'sended':False})
            return render(request, 'registration/registration_complete.html',
                          {'form':form, 'sended':True})
    else:
        form = UserCreationCaptchaForm()
    return render(request, 'registration/registration_form.html', {'form':form})



def signup_confirm(request, uidb64, token):
    token_generator = signup_token_generator
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    post_signup_redirect = 'registration/signup_confirm.html'
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token) and user.is_active == False:
        validlink = True
        user.is_active = True
        user.save()
        context = {
                'validlink': validlink,        
                'username': user.username,
        }        
        return render(request, post_signup_redirect, context)
    else:
        validlink = False
    context = {
        'validlink': validlink,
    }
    
    return render(request, post_signup_redirect, context)

@login_required
def email_change(request):
    post_change_redirect = 'registration/email_change_form.html'
    if request.method == "POST":
        form = ChangeEmailForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context = {
                'done': 'Done!',
            }
            return render(request, post_change_redirect, context)
    else:
        form = ChangeEmailForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, post_change_redirect, context)


@login_required
def delete_account(request):
    post_delete_redirect = 'registration/delete_account_form.html'
    if request.method == "POST":
        form = DeleteAccountForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.delete()
            logout(request)
            context = {
                    'done': 1,
                    }
            return render(request, post_delete_redirect, context)
    else:
        form = DeleteAccountForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, post_delete_redirect, context)


@login_required
def contact_login(request):
    contact_login_redirect = 'registration/contact_login_form.html'
    if request.method == "POST":
        form = ContactLoginForm(request.POST)
        if form.is_valid():
            body = "User: {user} / {email} said: ".format(
                    user=request.user.username,
                    email=request.user.email)
            body += "\n\n{0}".format(form.cleaned_data.get('message'))
            if send_mail(subject='Contact: ' + form.cleaned_data.get('subject').strip(),
                         message=body,
                         from_email=None,
                         recipient_list=[settings.EMAIL_HOST_USER]) != 1:
                    context = {
                            'email_fail': 'Fail!',
                            }
            else:
                context = {
                        'done': 'Done!',
                        }
            return render(request, contact_login_redirect, context)
    else:
        form = ContactLoginForm()
    context = {
            'form': form,
            }
    return render(request, contact_login_redirect, context)


def contact(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/contact/login')
    else:
        contact_redirect = 'registration/contact_form.html'
        if request.method == "POST":
            form = ContactForm(request.POST)
            if form.is_valid():
                body = "Anonymous: {name} / {email} said: ".format(
                    name=form.cleaned_data.get('name'),
                    email=form.cleaned_data.get('email_to_respond'))
                body += "\n\n{0}".format(form.cleaned_data.get('message'))
                if send_mail(subject='Contact: ' + form.cleaned_data.get('subject').strip(),
                         message=body,
                         from_email=None,
                         recipient_list=[settings.EMAIL_HOST_USER]) != 1:
                    context = {
                            'email_fail': 'Fail!',
                            }
                else:
                    context = {
                            'done': 'Done!',
                        }
                return render(request, contact_redirect, context)
        else:
            form = ContactForm()
        context = {
            'form': form,
            }
        return render(request, contact_redirect, context)

