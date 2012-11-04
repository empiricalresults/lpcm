# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from lpcm import LargePersistentCachedMap
from lcm import LargeCachedMap
from lpm import LargePersistentMap
from models import Signals
from key import LPCMKey

class LargePersistentCachedMapForSets(LargePersistentCachedMap):
  """ LPCM with convenience for maps of type key:set(v1, v2)
    m["key1"] = ["a", "b", "c"]
    m["key2"] = set([1, 2])
    Supports atomic insertion and removing of values:
    m.insert_values("key1", set(["d", "e"]))
    LPCMSets return empty sets for non-existent keys
    m["new-key"] returns set()
  """

  def __init__(self, name, cache_timeout=None):
    "When cache_only is true, the data will be stored in memcached only (used in tests)"
    super(LargePersistentCachedMapForSets, self).__init__(name)
    self.lpm = LargePersistentMapForSets(name)

  def __setitem__(self, key, value):
    return super(LargePersistentCachedMapForSets, self).__setitem__(key, set(value))

  def __getitem__(self, key):
    "Return empty set for non-existent keys"
    try:
      return super(LargePersistentCachedMapForSets, self).__getitem__(key)
    except KeyError:
      return set()


  def insert_values(self, key, values):
    self._atomic_add_value(key, set(values))

  def remove_values(self, key, values):
    self._atomic_delete_values(key, set(values))

  def increment(self, key, value = 1):
    raise NotImplementedError

  def decrement(self, key, value = 1):
    raise NotImplementedError

class LargeCachedMapForSets(LargeCachedMap):
  """Cached-only version of LPCMSet"""
  def __setitem__(self, key, value):
    return super(LargeCachedMapForSets, self).__setitem__(key, set(value))

  def __getitem__(self, key):
    "Return empty set for non-existent keys"
    try:
      return super(LargeCachedMapForSets, self).__getitem__(key)
    except KeyError:
      return set()

  def insert_values(self, key, values):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.cache.atomic_update(cmp_key.cache_key, values,
      update_operator = set.union, default_value = set())
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def remove_values(self, key, values):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.cache.atomic_update(cmp_key.cache_key, values,
      update_operator = set.difference, default_value = set())
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def increment(self, key, value = 1):
    raise NotImplementedError

  def decrement(self, key, value = 1):
    raise NotImplementedError

class LargePersistentMapForSets(LargePersistentMap):
  """Persistent later of LPCMForSets. Pre and post processing enables empty sets"""
  def _preprocess_value_before_ddb_save(self, value):
    if not value:
      value = "__empty_set__"  # cannot send empty set to dynamodb
    return value

  def _postprocess_value_after_ddb_load(self, value):
    if value == "__empty_set__":
      value = set()
    return value
