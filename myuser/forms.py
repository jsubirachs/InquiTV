from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from myuser.models import MyUser
from captcha.fields import CaptchaField
#from django.core import validators


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserCreationCaptchaForm(UserCreationForm):
    # The same as UserCreationForm with captcha. Needed if you don't
    # want captcha in admin add user form but want in singup form.
    captcha = CaptchaField()
    

'''class ChangeEmailForm(forms.Form):
    """
    A form that lets a user change their email by entering their password.
    """
    error_messages = {
        'bad_password': "The password is incorrect.",
        'unique_email': "A user with that email already exists."
    }
    password = forms.CharField(label="Enter your password",
                                    widget=forms.PasswordInput)
    new_email = forms.EmailField(
        help_text='This email must be unique in this web.',
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      'Enter a valid email. '
                                      'This value may contain only letters, numbers '
                                      'and @/./+/-/_ characters.', 'invalid'),
        ],)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean_new_email(self):
        password = self.cleaned_data.get('password')
        new_email = self.cleaned_data.get('new_email')
        if password and new_email:
            if not self.user.check_password(password):
                raise forms.ValidationError(
                    self.error_messages['bad_password'],
                    code='bad_password',
                )
            if MyUser.objects.filter(email=new_email).exists():
                raise forms.ValidationError(
                self.error_messages['unique_email'],
                code='unique_email',
                )
        return new_email

    def save(self):
        self.user.email = self.cleaned_data['new_email']
        self.user.save()
        return self.user
'''

class ChangeEmailForm(forms.ModelForm):
    """
    A form that lets a user change their email by entering their password.
    """
    error_messages = {
        'bad_password': "The password is incorrect.",
    }
    password_check = forms.CharField(label="Enter your password",
                                    widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('password_check', 'email',)
        help_texts = {
            'email': 'This email must be unique in this web.',
            }

    def clean_password_check(self):
        password_check = self.cleaned_data.get('password_check')
        if not self.instance.check_password(password_check):
            raise forms.ValidationError(
                self.error_messages['bad_password'],
                code='bad_password',
            )
        return password_check


class DeleteAccountForm(forms.Form):
    """
    A form that lets a user delete their account by entering their password.
    """
    error_messages = {
        'bad_password': "The password is incorrect.",    
    }
    password = forms.CharField(label="Enter your password",
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError(
                self.error_messages['bad_password'],
                code='bad_password',
            )


class ContactLoginForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class ContactForm(forms.Form):
    name = forms.CharField()
    email_to_respond = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()
