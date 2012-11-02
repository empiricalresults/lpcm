# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt
import numbers
import operator
import time
import base64
from django.conf import settings
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError
from dynamodb import DynamoDB, DynamoDBKey
from thread_local import is_in_test
import config


class LargePersistentMap(object):
  """ The DynamoDB layer of the LPCM. Most people probably don't need to use this.
    Create a map by simply calling the constructor with the map name.
    Supported value types are strings and numbers. Maximum value size is 60kb.

    m = LargePersistentMap("my_table")
    m["key1"] = "some string"
    m["key2"] = set(["d", "e"])
    m2 = LargePersistentMap("my_table")
    print m2["key1"]
  """

  def __init__(self, name):
    self.name = name

  def __setitem__(self, key, value):
    ddb_key = self.generate_ddb_key(key)
    value = self._preprocess_value_before_ddb_save(value)
    item = DynamoDB.create_item(ddb_key)
    item['value'] = value
    item.put()

  def __getitem__(self, key):
    ddb_key = self.generate_ddb_key(key)
    try:
      item = DynamoDB.get_item(ddb_key)
    except DynamoDBKeyNotFoundError:
      raise KeyError(u"{name}:{key}".format(name = self.name, key = ddb_key.original_key_obj))
    value = item['value']
    value = self._postprocess_value_after_ddb_load(value)
    return value

  def __contains__(self, key):
    try:
      v = self[key]
    except KeyError:
      return False
    return True

  def generate_ddb_key(self, key):
    if isinstance(key, str) or isinstance(key, unicode):
      range_key = key
    else:
      range_key = repr(key) # so you we have tuple and other obj keys
    range_key =  base64.b32encode(range_key.encode('utf-8'))
    hash_key = self._get_ddb_hash_key()
    cache_key = "{hash_key}_{range_key}".format(hash_key = hash_key, range_key = range_key)
    return DynamoDBKey(
      hash_key = self._get_ddb_hash_key(),
      range_key = range_key,
      cache_key = cache_key,
      original_key_obj = key,
    )

  def _get_ddb_hash_key(self):
    hash_key = self.name
    if is_in_test():
      hash_key = u"__test_{hash_key}".format(hash_key = hash_key)
    return hash_key

  def delete(self, key):
    "Deletes a key-value map from dynamodb. Ignores it if item does not exist"
    ddb_key = self.generate_ddb_key(key)
    try:
      item = DynamoDB.get_item(ddb_key)
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
    ddb_key = self.generate_ddb_key(key)
    try:
      item = DynamoDB.get_item(ddb_key)
    except DynamoDBKeyNotFoundError:
      item = DynamoDB.create_item(ddb_key)
    item.add_attribute('value', value)
    item.save()

  def __iter__(self):
    "Note: this method is EXPENSIVE! PLease only use if absolutely needed"
    ddb_key = self.generate_ddb_key('dummy_key')
    result = DynamoDB.query(ddb_key, attributes_to_get = ['table', 'key'])
    for item in result:
      key = item['key']
      yield base64.b32decode(key).decode('utf-8')

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

  def _preprocess_value_before_ddb_save(self, value):
    return value

  def _postprocess_value_after_ddb_load(self, value):
    return value

  def clear(self):
    raise NotImplementedError

  def copy(self):
    raise NotImplementedError


class MockLPM(LargePersistentMap):
  """ A mock object used instead of LPM in cached-only LPCM """

  def __setitem__(self, key, value):
    pass

  def __getitem__(self, key):
    raise KeyError()

  def __contains__(self, key):
    return False

  def delete(self, key):
    pass

  def increment(self, key, value = 1):
    pass

  def decrement(self, key, value = 1):
    pass

  def _atomic_add_value(self, key, value):
    pass

  def __iter__(self):
    raise NotImplementedError

  def items(self):
    raise NotImplementedError

  def get(self, k, d = None):
    raise NotImplementedError

  def iteritems(self): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def iterkeys(self): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def itervalues(self): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def keys(self): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def pop(self, k, d=None): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def values(self): # real signature unknown; restored from __doc__
    raise NotImplementedError

  def clear(self):
    raise NotImplementedError

  def copy(self):
    raise NotImplementedError

