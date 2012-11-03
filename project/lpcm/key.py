import base64
from thread_local import is_in_test

class LPCMKey(object):
  """Represents a composite key used by dynamo-db and memcached"""
  def __init__(self, map_name, key):
    self.original_key_obj = key
    if isinstance(key, str) or isinstance(key, unicode):
      self.original_key_str = key
    else:
      self.original_key_str = repr(key) # so you we have tuple and other obj keys
    self.range_key =  base64.b32encode(self.original_key_str.encode('utf-8'))
    self.hash_key = self._get_ddb_hash_key(map_name)

  def _get_ddb_hash_key(self, map_name):
    hash_key = map_name
    if is_in_test():
      hash_key = u"__test_{hash_key}".format(hash_key = hash_key)
    return hash_key

  @property
  def cache_key(self):
    #noinspection PyTypeChecker
    return "{self.hash_key}_{self.range_key}".format(self = self)
