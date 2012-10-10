# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

LPCM_CACHE_TIMEOUT = getattr(settings, 'LPCM_CACHE_TIMEOUT', 0)
LPCM_TEST_USE_LOCAL_CACHE_ONLY = getattr(settings, 'LPCM_TEST_USE_LOCAL_CACHE_ONLY', True)
LPCM_DEBUG_USE_LOCAL_CACHE_ONLY = getattr(settings, 'LPCM_DEBUG_USE_LOCAL_CACHE_ONLY', False)
LPCM_DYNAMODB_TABLE_NAME = getattr(settings, 'LPCM_DYNAMODB_TABLE_NAME', "lpcm")
try:
  DYNAMODB_ACCESS_KEY = settings.LPCM_DYNAMODB_ACCESS_KEY
except AttributeError:
  raise ImproperlyConfigured("LPCM Config Error: " +
    "Please define a value for LPCM_DYNAMODB_ACCESS_KEY in your settings file")


try:
  DYNAMODB_SECRET_ACCESS_KEY = settings.LPCM_DYNAMODB_SECRET_ACCESS_KEY
except AttributeError:
  raise ImproperlyConfigured("LPCM Config Error: " +
    "Please define a value for LPCM_DYNAMODB_SECRET_ACCESS_KEY in your settings file")


LPCM_PROVISIONED_THROUGHPUT = getattr(settings, 'LPCM_PROVISIONED_THROUGHPUT',
  {
  'read_units': 10,
  'write_units': 10
  })
