DEBUG = True

INSTALLED_APPS = (
    'project.lpcm'
)

LPCM_DYNAMODB_ACCESS_KEY = None # "** Your DynamoDB Access Key **"
LPCM_DYNAMODB_SECRET_ACCESS_KEY = None # "** Your DynamoDB Secret Access Key **"
LPCM_DYNAMODB_PROVISIONED_READ_UNITS = 10
LPCM_DYNAMODB_PROVISIONED_WRITE_UNITS = 10

LPCM_TEST_USE_LOCAL_CACHE_ONLY = False  
LPCM_DEBUG_USE_LOCAL_CACHE_ONLY = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    },
}

DATABASES = { # needed to run the tests
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lpcm.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

try:
  from settings_local import *
except ImportError:
  pass
