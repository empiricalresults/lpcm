# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import numbers
import time
from cache import Cache, CacheDisabled
from lpm import LargePersistentMap
from models import Signals
from key import LPCMKey

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

  def __init__(self, name, cache_timeout = None):
    "When cache_only is true, the data will be stored in memcached only (used in tests)"
    self.name = name
    self.lpm = LargePersistentMap(name)
    self.cache = Cache(cache_timeout)

  def __setitem__(self, key, value):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.cache.set(cmp_key.cache_key, value)
    self.lpm[key] = value
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def __getitem__(self, key):
    cmp_key = LPCMKey(self.name, key)
    v = self.cache.get(cmp_key.cache_key)
    if v is not None:
      return v
    return self._get_from_dynamodb_and_save_in_cache(cmp_key)

  def get(self, k, d = None):
    """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. """
    try:
      return self[k]
    except KeyError:
      return d

  def __contains__(self, key):
    try:
      v = self[key]
    except KeyError:
      return False
    return True

  def disable_caching(self):
    self.cache = CacheDisabled()

  def _get_from_dynamodb_and_save_in_cache(self, cmp_key):
    """ Gets value from dynamodb and puts it in cache, taking care of the cache-miss stampede """
    if self.cache.get_thread_safe_token(cmp_key.cache_key):
      # we got the token. i'll get it from db while other threads wait!
      value = self.lpm[cmp_key.original_key_obj]
      self.cache.set(cmp_key.cache_key, value)
      return value
    # someone is already getting it
    time.sleep(1) # wait a little, and get it again (hopefully from cache)
    return self.__getitem__(cmp_key.original_key_obj)

  def delete(self, key):
    "Deletes a key-value map from memcached and dynamodb. Ignores it if item does not exist"
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'delete')
    cmp_key = LPCMKey(self.name, key)
    self.cache.delete(cmp_key.cache_key)
    self.lpm.delete(key)
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'delete')

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
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.lpm.atomic_add_value(key, value)
    self.cache.delete(cmp_key.cache_key)
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def _atomic_delete_values(self, key, values):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.lpm.atomic_delete_values(key, values)
    self.cache.delete(cmp_key.cache_key)
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def __iter__(self):
    """ Note: this method is EXPENSIVE! PLease only use if absolutely needed"""
    return self.lpm.__iter__()

  def items(self):
    """ Note: this method is EXPENSIVE! PLease only use if absolutely needed"""
    return [(k, self[k]) for k in self]

  def keys(self):
    """ Note: this method is EXPENSIVE! PLease only use if absoluely needed"""
    return [k for k in self]

  def pop(self, k, d = None):
    """
    D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
    If key is not found, d is returned if given, otherwise KeyError is raised
    """
    pass

  def clear(self):
    raise NotImplementedError()

  def copy(self):
    raise NotImplementedError()

