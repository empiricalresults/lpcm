from collections import namedtuple
from thread_local import  lpcm_thread_local, is_in_test
from models import Signals as LPCMSignal


MapRecord = namedtuple('MapRecord', field_names = ['map_name', 'map_class'])

class LPCMCleanUp(object):
  """ Keeps track of all the maps updated in test threads (once .bind() is called
      Can clean up all keys for all updated tables using the full_cleanup()
  """
  @classmethod
  def bind(cls):
    assert is_in_test(), "Should only call this in a test thread"
    LPCMSignal.post_update.connect(receiver = on_map_update)

  @classmethod
  def full_clean_up(cls):
    updated_maps = cls._get_updated_maps()
    for map_record in updated_maps:
      KLS = map_record.map_class
      map = KLS(name = map_record.map_name)
      for k in map.keys():
        map.delete(k)

  @classmethod
  def add_map_record(cls, map_class, map_name):
    updated_maps = cls._get_updated_maps()
    map_record = MapRecord(map_class = map_class, map_name = map_name)
    updated_maps.add(map_record)

  @classmethod
  def _get_updated_maps(cls):
    try:
      return lpcm_thread_local.updated_maps
    except AttributeError:
      lpcm_thread_local.updated_maps = set()
    return lpcm_thread_local.updated_maps


def on_map_update(sender, **kwargs):
  if not is_in_test():
    return
  map_name = kwargs['map_name']
  LPCMCleanUp.add_map_record(map_class = sender, map_name = map_name)