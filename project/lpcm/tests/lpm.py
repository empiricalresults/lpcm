# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import unittest
from django.core.cache import cache
from base import LPCMTestCase
from ..lpm import LargePersistentMap as LPM
from .. import config

@unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
class TestLPM(LPCMTestCase):

  def setUp(self):
    super(TestLPM, self).setUp()
    cache.clear()

  def test_get(self):
    some_map = LPM(name = "some_map")
    another_map = LPM(name = "another_map")
    some_map["a"] = 123
    some_map["b"] = "some string"
    some_map["c"] = 7.890
    another_map["a"] = 321
    another_map["b"] = "another string"
    another_map["c"] = 8.901
    try:
      self.assertEquals(some_map["a"], 123)
      self.assertEquals(some_map["b"], "some string")
      self.assertEquals(some_map["c"], 7.890)
      self.assertEquals(another_map["a"], 321)
      self.assertEquals(another_map["b"], "another string")
      self.assertEquals(another_map["c"], 8.901)
    finally:
      some_map.delete("a")
      some_map.delete("b")
      some_map.delete("c")
      another_map.delete("a")
      another_map.delete("b")
      another_map.delete("c")
    with self.assertRaises(KeyError):
      a = some_map["bad_key"]

  def test_contains(self):
    some_map = LPM(name = "some_map")
    try:
      some_map["a"] = 123
      self.assertIn('a', some_map)
      self.assertNotIn('bad_key', some_map)
    finally:
      some_map.delete("a")

  def test_delete(self):
    some_map = LPM(name = "some_map")
    some_map["a"] = 123
    self.assertEquals(some_map["a"], 123)
    some_map.delete("a")
    with self.assertRaises(KeyError):
      a = some_map["a"]
      # deleting non existent key should be fine
    some_map.delete("lala_i_don't_exist")

  def test_unicode(self):
    some_map = LPM(name = "some_map")
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    unicode_value = 'Ivan Krsti\xc4\x87 is unicode'.decode('utf8')
    try:
      some_map[unicode_key] = unicode_value
      self.assertEquals(some_map[unicode_key], unicode_value)
    finally:
      some_map.delete(unicode_key)

  def test_increment(self):
    some_map = LPM(name = "some_map")
    try:
      some_map['a'] = 41
      some_map.atomic_add_value('a', -1)
      self.assertEquals(some_map['a'], 40)
      some_map.atomic_add_value('a', 4.2)
      self.assertEquals(some_map['a'], 44.2)
    finally:
      some_map.delete('a')

  def test_increment_non_existent(self):
    some_map = LPM(name = "some_map")
    try:
      some_map.atomic_add_value('new_key', 1)
      self.assertEquals(some_map['new_key'], 1)
      some_map.atomic_add_value('another_key', 10)
      self.assertEquals(some_map['another_key'], 10)
    finally:
      some_map.delete('new_key')
      some_map.delete('another_key')

  def test_bad_increment_regular(self):
    some_map = LPM(name = "some_map")
    try:
      with self.assertRaises(ValueError):
        some_map.atomic_add_value('new_key', 'bcde')
    finally:
      some_map.delete('new_key')


  def test_iter(self):
    some_map = LPM(name = "some_map")
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    try:
      some_map["a"] = 123
      some_map["b"] = "some string"
      some_map["c"] = 7.890
      some_map[unicode_key] = u"you are always a pain unicode"
      keys = set([k for k in some_map])
      self.assertEquals(keys, {'a', 'b', 'c', unicode_key})
    finally:
      some_map.delete("a")
      some_map.delete("b")
      some_map.delete("c")
      some_map.delete(unicode_key)