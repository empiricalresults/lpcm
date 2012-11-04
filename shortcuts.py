from django.conf import settings
import config
from thread_local import is_in_test

def LPCM(name, cache_only = False, cache_timeout = None):
  if cache_only or force_cache_only():
    from lcm import LargeCachedMap
    return LargeCachedMap(name, cache_timeout)
  else:
    from lpcm import LargePersistentCachedMap
    return LargePersistentCachedMap(name, cache_timeout)

def LPCMSet(name, cache_only = False, cache_timeout = None):
  if cache_only or force_cache_only():
    from lpcm_set import LargePersistentCachedMapForSets
    return LargePersistentCachedMapForSets(name, cache_timeout)
  else:
    from lpcm_set import LargeCachedMapForSets
    return LargeCachedMapForSets(name, cache_timeout)

def force_cache_only():
  if is_in_test():
    return config.LPCM_TEST_USE_LOCAL_CACHE_ONLY
  if settings.DEBUG:
    return config.LPCM_DEBUG_USE_LOCAL_CACHE_ONLY
  return False