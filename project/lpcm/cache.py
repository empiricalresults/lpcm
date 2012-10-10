from django.core.cache import get_cache, InvalidCacheBackendError
from django.core.cache import cache as default_cache
import config

try:
  LPCM_CACHE = get_cache('lpcm')
except InvalidCacheBackendError:
  LPCM_CACHE  = default_cache

class Cache(object):

  def __init__(self, timeout):
    if timeout is None:
      timeout = config.LPCM_CACHE_TIMEOUT
    self.timeout = timeout

  def get(self, key):
    return LPCM_CACHE.get(key)

  def set(self, key, value):
    return LPCM_CACHE.set(key, value, self.timeout)

  def delete(self, key):
    return LPCM_CACHE.delete(key)

  def get_thread_safe_token(self, key):
    "Returns True if we can get a thread-safe token to update a given key"
    key_token =  "{key}_thread_safe_token".format(key = key)
    timeout = 2 # expected time for a dynamo-db transaction
    if self.timeout:
      timeout = min(timeout, self.timeout)
    return LPCM_CACHE.add(key_token, True, timeout)

  def atomic_update(self, key, update_value, update_operator, default_value):
    """ Performs an atomic update to a cached value, using CAS (Compare And Swap)
    If there is no current value for the given key, default_value will be used """
    curr_val = LPCM_CACHE.get(key)
    if curr_val is None:
      curr_val = default_value
    new_value = update_operator(curr_val, update_value)
    cas_key = LPCM_CACHE.make_key(key)
    success = LPCM_CACHE._cache.cas(cas_key, new_value)
    if not success: # another thread just changed this :/ lets try again
      self.atomic_update(key, update_value, update_operator, default_value)

class CacheDisabled(object):
  "A dummy cache object that doesn't cache at all. used to diable caching"

  def get(self, key):
    return None

  def set(self, key, value):
    return None

  def delete(self, key):
    return None

  def get_thread_safe_token(self, key):
    return True

  def atomic_update(self, key, update_value, update_operator, default_value):
    return None
