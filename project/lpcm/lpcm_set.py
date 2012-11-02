# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from lpcm import LargePersistentCachedMap

class LPCMSet(LargePersistentCachedMap):
  """ A dictionary of key => set(val1, val2, ..., val_k)
    which is saved both in Memcached and AWS DynamoDB.
    Create a map by simply calling the constructor with the map name.

    m = LargePersistentCachedMap("my_table")
    m["key1"] = set(["a", "b", "c"])
    m["key2"] = set([1, 2])

    LPCMSet supports atomic insertion and removing of values:
    m.insert_values("key1", set(["d", "e"]))

  """

  def __setitem__(self, key, value):
    return super(LPCMSet, self).__setitem__(key, set(value))

  def _preprocess_value_before_ddb_save(self, value):
    if len(value) < 1:
      value = "__empty_set__"  # cannot send empty set to dynamodb
    return value

  def _postprocess_value_after_ddb_load(self, value):
    if value == "__empty_set__":
      value = set()
    return value

  def insert_values(self, key, values):
    "Appends the set of strings to the current list"
    self._atomic_add_value(key, set(values))

  def _atomic_add_value_to_cache(self, ddb_key, value):
    self.cache.atomic_update(ddb_key.cache_key, value,
      update_operator = set.union, default_value = set())

  def increment(self, key, value = 1):
    raise NotImplementedError

  def decrement(self, key, value = 1):
    raise NotImplementedError
