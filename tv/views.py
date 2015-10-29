from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from constance import config
import datetime
from django.core.cache import cache
from django.contrib import messages
#Funcion payment_check
import imaplib
from email import message_from_bytes
from base64 import b64decode
from urllib.parse import unquote
from bs4 import BeautifulSoup


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/tv/')
    else:
        return login(request)


def user_access_tv(request):
    #4h for expiry tv cache
    seconds_expiry = 60*60*4

    if cache.get('tv'):
        if request.session.session_key in cache.get('tv'):
            return True
    else:
        cache.set('tv', [], seconds_expiry)

    # verificar si tiene saldo, free_access, acceso universal o admin
    if request.user.profile.buy_date is not None:
        buy_date = (datetime.date.today() - request.user.profile.buy_date).days < config.V6_SUBSCRIPTION_DAYS
    else:
        buy_date = False

    if buy_date or request.user.profile.free_access or request.user.is_admin or config.V7_WORLD_FREE_ACCESS :
        lista = cache.get('tv')
        lista.append(request.session.session_key)
        cache.set('tv', lista, seconds_expiry)
        return True
    else:
        return False


@login_required
def tv(request):
    if user_access_tv(request):
        return render(request, 'tv/tv.html')
    else:
        return HttpResponseRedirect('/subscription/')
    
    
@login_required
def live(request):
    if user_access_tv(request):
        get_path = 'http://127.0.0.1:8080' + request.get_full_path()[5:]
        return HttpResponseRedirect(get_path)
    else:
        return False


def payment_check(user, payment_method):
    price = config.V4_PRICE
    currency = config.V5_CURRENCY
    method = {
        'PAYPAL': 'member@paypal.com',
        'NETELLER': 'noreply@neteller.com',
        'SKRILL': 'no-reply@email.skrill.com',
    }

    if payment_method.upper() not in method:
        print('Incorrect payment method!!')
        return False
    elif payment_method.lower() == 'paypal':
        cabecera = '(HEADER From "' + method[payment_method.upper()] + '" Subject "' + user + '")'
    else:
        cabecera = '(HEADER From "' + method[payment_method.upper()] + '")'


    mail = imaplib.IMAP4_SSL(config.V1_EMAIL_PAYMENT_HOST)
    mail.login(config.V2_EMAIL_PAYMENT_USER, config.V3_EMAIL_PAYMENT_PASSWORD)
    mail.select() #INBOX por default, aunque se puede especificar ('inbox')

    result, data = mail.uid('search', None, cabecera)
    #Si hay 1 hacer split() no es correcto
    #Si hay 2 o + estan separados por espacio y se puede hacer split()
    if b' ' in data[0]:
        data = data[0].split()
    
    #Si hay emails del payment_method buscamos coincidencias (user,price...)
    if len(data[0])>0:
        for num in data:
            result, msg = mail.uid('fetch', num, '(RFC822)')
            email_message = message_from_bytes(msg[0][1])
            # maintype = email_message.get_content_maintype()
            # if maintype == 'multipart':
            for part in email_message.get_payload():
                if part.get_content_maintype() == 'text':
                    if payment_method.lower() in ('paypal','neteller'):
                        email_html = b64decode(part.get_payload())
                        soup = BeautifulSoup(email_html, "html.parser")
                        email_txt = soup.get_text().replace('\n', ' ').lower()
                        if payment_method.lower() == 'neteller':
                            #pasar todo a lower para que coincida
                            cantidad = 'cantidad: ' + '{:.2f} '.format(price) + currency.lower()
                            mensaje = 'mensaje: ' + user.lower()
                        if payment_method.lower() == 'paypal':
                            cantidad = 'enviado €' + '{:.2f} '.format(price).replace('.',',') + currency.lower()
                    if payment_method.lower() == 'skrill':
                        soup = BeautifulSoup(part.get_payload(),"html.parser").get_text().lower()
                        #Para skrill (texto con acentos, etc)
                        email_txt = unquote(soup.replace('=\r\n','').replace('=','%').replace('\n',' '))
                        #Si tiene decimales los mostramos (1.50->1.5 / 1.55->1.55) sino los quitamos
                        cantidad = 'importe: ' + currency.lower() + ' {0}'.format(('{:.1f}'.format(price) if len(str(price).split('.')[1])==1 else '{:.2f}'.format(price)) if price % 1 else int(price))
                        mensaje = 'explicación: ' + user.lower()

                    if (payment_method.lower() == 'paypal' and cantidad in email_txt) or \
                       (cantidad in email_txt and mensaje in email_txt):
                        #Si el mail coincide, ponerlo en cobrados
                        #Comando 'MOVE' aun no implementado en imaplib:
                        #copy = mail.uid('move', num, 'Cobrados')
                        copy = mail.uid('copy', num, 'Cobrados')
                        #Esto sobraria con el comando 'MOVE':
                        if copy[0] == 'OK':
                            mov, copy = mail.uid('STORE', num , '+FLAGS', '(\Deleted)')
                            mail.expunge()
                            mail.close()
                            mail.logout()
                            print('Encontrado!')
                            return True
                        else:
                            print("Error moving email to 'Cobrados'")

            #Si el mail no coincide, ponerlo como no leido de nuevo
            mail.uid('store', num, '-FLAGS', '\\SEEN')

            # elif maintype == 'text':
            #     return email_message.get_payload()
    print('No hay emails')
    return False


@login_required
def subscription(request):
    user = request.user
    subscription_template = 'tv/subscription.html'
    if request.method == "POST":
        if payment_check(user.username,request.POST['method']):
            user.profile.buy_date = datetime.date.today()
            user.profile.save()
            return HttpResponseRedirect('/tv/')
        else:
            messages.error(request, "Error, payment undetected!")
    context = {
        'config': config,
    }
    return render(request, subscription_template, context)


