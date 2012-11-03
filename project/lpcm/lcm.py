import operator
from django.dispatch import receiver
from lpcm import LargePersistentCachedMap
from lpm import MockLPM
from models import Signals
from key import LPCMKey

class LargeCachedMap(LargePersistentCachedMap):
  """The Cached-only version of LPCM. Used in tests and debug"""

  def __init__(self, name, cache_timeout = None):
    super(LargeCachedMap, self).__init__(name, cache_timeout)
    self.lpm = MockLPM()

  def __setitem__(self, key, value):
    super(LargeCachedMap, self).__setitem__(key, value)

  def disable_caching(self):
    raise NotImplementedError("cannot have a cache-only map with caching disabled")

  def _atomic_add_value(self, key, value):
    Signals.pre_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')
    cmp_key = LPCMKey(self.name, key)
    self.cache.atomic_update(cmp_key.cache_key, value,
      update_operator = operator.add, default_value = 0)
    Signals.post_update.send(sender = self.__class__, map_name = self.name, key = key, action = 'put')

  def __iter__(self):
    return LCMKeys.get_keys(map_name = self.name).__iter__()

class LCMKeys(object):
  """Enables cached-only LPCM maps to keep track of their keys"""
  class Constants(object):
    LCMSET_NAME = "__lcm_keys"

  @classmethod
  def add_key(cls, map_name, key):
    map_keys = cls._get_keys_map()
    map_keys.insert_values(key = map_name, values = [key])

  @classmethod
  def remove_key(cls, map_name, key):
    map_keys = cls._get_keys_map()
    map_keys.remove_values(key = map_name, values = [key])

  @classmethod
  def get_keys(cls, map_name):
    map_keys = cls._get_keys_map()
    return map_keys[map_name]

  @classmethod
  def _get_keys_map(cls):
    "Returns a cached-only LCPMSet which maps map-names to their current keys"
    from lpcm_set import LargeCachedMapForSets as LCMSet
    return LCMSet("__lcm_keys")


@receiver(Signals.post_update)
def on_lcm_update(sender, **kwargs):
  if not issubclass(sender, LargeCachedMap):
    return
  action = kwargs['action']
  map_name = kwargs['map_name']
  if map_name == LCMKeys.Constants.LCMSET_NAME:
    return # this would cause a nasty recursion!
  key = kwargs['key']
  if action == 'put':
    LCMKeys.add_key(map_name, key)
  elif action == 'delete':
    LCMKeys.remove_key(map_name, key)
  map_name = kwargs['map_name']
  key = kwargs['key']
