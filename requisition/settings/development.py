from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'requisition2',
        'USER': 'shfaria',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}