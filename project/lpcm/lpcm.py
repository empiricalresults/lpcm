# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import numbers
import operator
import time
import base64
from django.conf import settings
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError
from dynamodb import DynamoDB
from cache import Cache, CacheDisabled
from thread_local import is_in_test
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
    self.cache_only = cache_only or self._force_cache_only()
    self.cache = Cache(cache_timeout)

  def __setitem__(self, key, value):
    self.cache.set(self._get_cache_key(key), value)
    if self.cache_only:
      return
    value = self._preprocess_value_before_ddb_save(value)
    item = self._create_new_item(key)
    item['value'] = value
    item.put()

  def __getitem__(self, key):
    hash_key = self._get_cache_key(key)
    v = self.cache.get(hash_key)
    if v is not None:
      return v
    if self.cache_only:
      raise KeyError("{name}:{key}".format(name = self.name, key = key))
    return self._get_from_dynamodb_and_save_in_cache(key)

  def disable_caching(self):
    assert not self.cache_only, "cannot have a cache-only map with caching disabled"
    self.cache = CacheDisabled()

  def _force_cache_only(self):
    if is_in_test():
      return config.LPCM_TEST_USE_LOCAL_CACHE_ONLY
    if settings.DEBUG:
      return config.LPCM_DEBUG_USE_LOCAL_CACHE_ONLY
    return False

  def _get_ddb_key(self, key):
    if not isinstance(key, str) and not isinstance(key, unicode):
      key = repr(key) # so you we have tuple and other obj keys
    if is_in_test():
      key = u"__test_{key}".format(key = key)
    key = base64.b32encode(key.encode('utf-8'))

  def _get_cache_key(self, key):
    return "{name}_{key}".format(name = self.name, key = self._get_ddb_key(key))

  def _get_ddb_item(self, key):
    "Tries to get an item from DynamoDB. Throws DynamoDBKeyNotFoundError"
    table = DynamoDB.get_table(config.LPCM_DYNAMODB_TABLE_NAME)
    ddb_key = self._get_ddb_key(key)
    return table.get_item(hash_key = ddb_key, range_key = self.name)

  def _create_new_item(self, key):
    table = DynamoDB.get_table(config.LPCM_DYNAMODB_TABLE_NAME)
    ddb_key = self._get_ddb_key(key)
    return table.new_item(hash_key = ddb_key, range_key = self.name)

  def _preprocess_value_before_ddb_save(self, value):
    return value

  def _postprocess_value_after_ddb_load(self, value):
    return value

  def _get_from_dynamodb_and_save_in_cache(self, key):
    """ Gets value from dynamodb and puts it in cache, taking care of the cache-miss stampede """
    cache_key = self._get_cache_key(key)
    if self.cache.get_thread_safe_token(cache_key):
      # we got the token. i'll get it from db while other threads wait!
      return self._get_from_dynamodb_and_save_in_cache_stampede_solved(key)
    # crap! someone is already getting it
    time.sleep(1) # wait a little, and get it again (possibly from cache)
    return self.__getitem__(key)

  def _get_from_dynamodb_and_save_in_cache_stampede_solved(self, key):
    """ Gets value from dynamodb and puts it in cache,
      after the cache-miss stampede has been taken care of"""
    try:
      item = self._get_ddb_item(key)
    except DynamoDBKeyNotFoundError:
      raise KeyError("{name}:{key}".format(name = self.name, key = key))
    value = item['value']
    value = self._postprocess_value_after_ddb_load(value)
    cache_key = self._get_cache_key(key)
    self.cache.set(cache_key, value)
    return value

  def delete(self, key):
    "Deletes a key-value map from memcached and dynamodb. Ignores it if item does not exist"
    cache_key = self._get_cache_key(key)
    self.cache.delete(cache_key)
    if self.cache_only:
      return
    try:
      item = self._get_ddb_item(key)
    except DynamoDBKeyNotFoundError:
      return  # delete fails silently
    item.delete()

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
    if self.cache_only:
      self._atomic_add_value_to_cache(key, value)
      return
    self._atomic_add_value_to_dynamodb(key, value)
    self.cache.delete(self._get_cache_key(key))  # invalidate cache

  def _atomic_add_value_to_dynamodb(self, key, value):
    try:
      item = self._get_ddb_item(key)
    except DynamoDBKeyNotFoundError:
      item = self._create_new_item(key)
    item.add_attribute('value', value)
    item.save()

  def _atomic_add_value_to_cache(self, key, value):
    cache_key = self._get_cache_key(key)
    self.cache.atomic_update(cache_key, value,
      update_operator = operator.add, default_value = 0)

  def __iter__(self):
    raise NotImplementedError

  def keys(self):
    raise NotImplementedError

  def values(self):
    raise NotImplementedError

  def itervalues(self):
    raise NotImplementedError

  def clear(self):
    raise NotImplementedError

  def copy(self):
    raise NotImplementedError
