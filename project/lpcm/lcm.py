import operator
from lpcm import LargePersistentCachedMap
from lpm import MockLPM
from models import Signals

class LargeCachedMap(LargePersistentCachedMap):
  """The Cached-only version of LPCM. Used in tests and debug"""

  def __init__(self, name, cache_timeout = None):
    super(LargeCachedMap, self).__init__(name, cache_timeout)
    self.lpm = MockLPM(name)

  def __setitem__(self, key, value):
    super(LargeCachedMap, self).__setitem__(key, value)

  def disable_caching(self):
    raise NotImplementedError("cannot have a cache-only map with caching disabled")

  def _atomic_add_value(self, key, value):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key)
    ddb_key = self.lpm.generate_ddb_key(key)
    self.cache.atomic_update(ddb_key.cache_key, value,
      update_operator = operator.add, default_value = 0)
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key)

