# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import numbers
import operator
import time
from django.conf import settings
from cache import Cache, CacheDisabled
from thread_local import is_in_test
from lpm import LargePersistentMap
import config


class LargePersistentCachedMap(object):
  """ A key:value dictionary  which is saved both in Memcached and AWS DynamoDB.
    Create a map by simply calling the constructor with the map name.
    Supported value types are strings and numbers. Maximum value size is 60kb.

    m = LargePersistentCachedMap("my_table")
    m["key1"] = "some string"
    m["key2"] = set(["d", "e"])31415
    m2 = LargePersistentCachedMap("my_table")
    print m2["key1"]
  """

  def __init__(self, name, cache_only = False, cache_timeout = None):
    "When cache_only is true, the data will be stored in memcached only (used in tests)"
    self.name = name
    self.lpm = LargePersistentMap(name)
    self.cache_only = cache_only or self._force_cache_only()
    self.cache = Cache(cache_timeout)

  def __setitem__(self, key, value):
    ddb_key = self.lpm.generate_ddb_key(key)
    self.cache.set(ddb_key.cache_key, value)
    if self.cache_only:
      # TODO self._update_cache_only_keys(key)
      return
    self.lpm[key] = value

  def __getitem__(self, key):
    ddb_key = self.lpm.generate_ddb_key(key)
    v = self.cache.get(ddb_key.cache_key)
    if v is not None:
      return v
    if self.cache_only:
      raise KeyError(u"{name}:{key}".format(name = self.name, key = key))
    return self._get_from_dynamodb_and_save_in_cache(ddb_key)

  def __contains__(self, key):
    try:
      v = self[key]
    except KeyError:
      return False
    return True

  def disable_caching(self):
    assert not self.cache_only, "cannot have a cache-only map with caching disabled"
    self.cache = CacheDisabled()

  def _force_cache_only(self):
    if is_in_test():
      return config.LPCM_TEST_USE_LOCAL_CACHE_ONLY
    if settings.DEBUG:
      return config.LPCM_DEBUG_USE_LOCAL_CACHE_ONLY
    return False

  def _get_from_dynamodb_and_save_in_cache(self, ddb_key):
    """ Gets value from dynamodb and puts it in cache, taking care of the cache-miss stampede """
    if self.cache.get_thread_safe_token(ddb_key.cache_key):
      # we got the token. i'll get it from db while other threads wait!
      value = self.lpm[ddb_key.original_key_obj]
      self.cache.set(ddb_key.cache_key, value)
      return value
    # someone is already getting it
    time.sleep(1) # wait a little, and get it again (hopefully from cache)
    return self.__getitem__(ddb_key.original_key_obj)

  def delete(self, key):
    "Deletes a key-value map from memcached and dynamodb. Ignores it if item does not exist"
    ddb_key = self.lpm.generate_ddb_key(key)
    self.cache.delete(ddb_key.cache_key)
    if self.cache_only:
      return
    self.lpm.delete(key)

  def increment(self, key, value = 1):
    if not isinstance(value, numbers.Number):
      raise ValueError(
        "Invalid increment value: {}. Only numbers are supported".format(value))
    self._atomic_add_value(key, value)

  def decrement(self, key, value = 1):
    if not isinstance(value, numbers.Number):
      raise ValueError(
        "Invalid decrement value: {}. Only numbers are supported".format(value))
    self._atomic_add_value(key, value * -1)

  def _atomic_add_value(self, key, value):
    ddb_key = self.lpm.generate_ddb_key(key)
    if self.cache_only:
      self.cache.atomic_update(ddb_key.cache_key, value,
        update_operator = operator.add, default_value = 0)
      return
    self.lpm.increment(key, value)
    self.cache.delete(ddb_key.cache_key)  # invalidate cache

  def __iter__(self):
    return self.lpm.__iter__()

  def items(self):
    """ D.items() -> list of D's (key, value) pairs, as 2-tuples """
  pass

  def get(self, k, d = None):
    """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. """
    try:
      return self[k]
    except KeyError:
      return d

  def iteritems(self): # real signature unknown; restored from __doc__
    """ D.iteritems() -> an iterator over the (key, value) items of D """
    pass

  def iterkeys(self): # real signature unknown; restored from __doc__
    """ D.iterkeys() -> an iterator over the keys of D """
    pass

  def itervalues(self): # real signature unknown; restored from __doc__
    """ D.itervalues() -> an iterator over the values of D """
    pass

  def keys(self): # real signature unknown; restored from __doc__
    """ D.keys() -> list of D's keys """
    return []

  def pop(self, k, d=None): # real signature unknown; restored from __doc__
    """
    D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
    If key is not found, d is returned if given, otherwise KeyError is raised
    """
    pass

  def values(self): # real signature unknown; restored from __doc__
    """ D.values() -> list of D's values """
    return []

  def clear(self):
    raise NotImplementedError

  def copy(self):
    raise NotImplementedError

class d(dict):
  pass