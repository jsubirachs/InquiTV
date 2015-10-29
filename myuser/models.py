from django.core import validators
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(username=username,
            email=self.normalize_email(email),
            date_joined=now
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email 
        and password.
        """
        user = self.create_user(username, email,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(
        verbose_name='username',
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.',
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                     'Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.', 'invalid'),
        ],
        error_messages={
            'unique': "A user with that username already exists.",
        })
    email = models.EmailField(
        verbose_name='email address',        
        unique=True,
        help_text='Required. This email must be unique in this web',
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        verbose_name='date joined',
        default=timezone.now
    )
    
    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their username
        return self.username

    def get_short_name(self):
        # The user is identified by their username
        return self.username

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
