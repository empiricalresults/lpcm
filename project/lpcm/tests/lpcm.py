# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import unittest
from django.core.cache import cache
from base import LPCMTestCase
from ..lpcm import LargePersistentCachedMap as LPCM
from .. import config
from project.lpcm.lpm import MockLPM

@unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
class TestLPCM(LPCMTestCase):

  def setUp(self):
    super(TestLPCM, self).setUp()
    cache.clear()

  def test_read_from_cache_and_db(self):
    some_map = LPCM(name = "some_map")
    another_map = LPCM(name = "another_map")
    some_map["a"] = 123
    some_map["b"] = "some string"
    some_map["c"] = 7.890
    another_map["a"] = 234
    another_map["b"] = "another string"
    another_map["c"] = 8.901
    # Make sure we can read from cache
    some_map_lpm = some_map.lpm
    another_map_lpm = another_map.lpm
    some_map.lpm = MockLPM('some_map')
    another_map.lpm = MockLPM('another_map')
    try:
      self.assertEquals(some_map["a"], 123)
      self.assertEquals(some_map["b"], "some string")
      self.assertEquals(some_map["c"], 7.890)
      self.assertEquals(another_map["a"], 234)
      self.assertEquals(another_map["b"], "another string")
      self.assertEquals(another_map["c"], 8.901)
      # Make sure we can read from DB Backend
      some_map.lpm = some_map_lpm
      another_map.lpm = another_map_lpm
      cache.clear()
      self.assertEquals(some_map["a"], 123)
      self.assertEquals(some_map["b"], "some string")
      self.assertEquals(some_map["c"], 7.890)
      self.assertEquals(another_map["a"], 234)
      self.assertEquals(another_map["b"], "another string")
      self.assertEquals(another_map["c"], 8.901)
    finally:
      some_map.delete("a")
      some_map.delete("b")
      some_map.delete("c")
      another_map.delete("a")
      another_map.delete("b")
      another_map.delete("c")

  def test_contains(self):
    some_map = LPCM(name = "some_map")
    try:
      some_map["a"] = 123
      self.assertIn('a', some_map)
      self.assertNotIn('bad_key', some_map)
    finally:
      some_map.delete("a")

  def test_delete(self):
    some_map = LPCM(name = "some_map")
    some_map["a"] = 123
    self.assertEquals(some_map["a"], 123)
    some_map.delete("a")
    with self.assertRaises(KeyError):
      a = some_map["a"]
    # deleting non existent key should be fine
    some_map.delete("lala_i_don't_exist")

  def test_unicode(self):
    some_map = LPCM(name = "some_map")
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    unicode_value = 'Ivan Krsti\xc4\x87 is unicode'.decode('utf8')
    try:
      some_map[unicode_key] = unicode_value
      self.assertEquals(some_map[unicode_key], unicode_value)
    finally:
      some_map.delete(unicode_key)

  def test_increment(self):
    some_map = LPCM(name = "some_map")
    try:
      some_map['a'] = 41
      some_map.increment('a')
      self.assertEquals(some_map['a'], 42)
      some_map.increment('a', 4.2)
      self.assertEquals(some_map['a'], 46.2)
    finally:
      some_map.delete('a')

  def test_increment_non_existent(self):
    some_map = LPCM(name = "some_map")
    try:
      some_map.increment('new_key')
      self.assertEquals(some_map['new_key'], 1)
      some_map.increment('another_key', 10)
      self.assertEquals(some_map['another_key'], 10)
    finally:
      some_map.delete('new_key')
      some_map.delete('another_key')

  def test_bad_increment(self):
    some_map = LPCM(name = "some_map")
    try:
      with self.assertRaises(ValueError):
        some_map.increment('new_key', 'bcde')
    finally:
      some_map.delete('new_key')

  def test_decrement(self):
    some_map = LPCM(name = "some_map")
    try:
      some_map['a'] = 43
      some_map.decrement('a')
      self.assertEquals(some_map['a'], 42)
      some_map.decrement('a', 1.9)
      self.assertEquals(some_map['a'], 40.1)
      some_map.decrement('a', 50.1)
      self.assertEquals(some_map['a'], -10)
    finally:
      some_map.delete('a')

  def test_disable_caching(self):
    some_map = LPCM(name = "some_map")
    from ..lcm import LargeCachedMap
    cache_only_map = LargeCachedMap(name = "some_map")
    try:
      some_map["a"] = 123
      cache_only_map.increment('a')
      self.assertEquals(some_map['a'], 124)  # reads from the incremented cash
      some_map.disable_caching()
      self.assertEquals(some_map['a'], 123)  # reads from the untouched dynamodb
    finally:
      some_map.delete("a")

  def test_iter(self):
    some_map = LPCM(name = "some_map")
    another_map = LPCM(name = "another_map")
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    try:
      some_map["a"] = 123
      some_map["b"] = "some string"
      some_map["c"] = 7.890
      another_map['a'] = 234
      another_map['d'] = 345
      another_map['e'] = 456
      some_map[unicode_key] = u"you are always a pain unicode"
      some_map_keys = set([k for k in some_map])
      self.assertEquals(some_map_keys, {'a', 'b', 'c', unicode_key})
      another_map.delete('e')
      another_map_keys = set([k for k in some_map])
      self.assertEquals(another_map_keys, {'a', 'd'})
    finally:
      some_map.delete("a")
      some_map.delete("b")
      some_map.delete("c")
      some_map.delete(unicode_key)
      another_map.delete("a")
      another_map.delete("d")
      another_map.delete("e")