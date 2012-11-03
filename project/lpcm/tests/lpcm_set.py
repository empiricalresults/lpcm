# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

import unittest
from django.core.cache import cache
from base import LPCMTestCase
from ..lpcm_set import LargePersistentCachedMapForSets as LPCMSet
from ..lpcm_set import  LargeCachedMapForSets as LCMSet
from .. import config

@unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
class TestLPCMSet(LPCMTestCase):
  def setUp(self):
    super(TestLPCMSet, self).setUp()
    cache.clear()

  def test_value_must_be_set(self):
    some_map = LPCMSet(name = "some_map")
    with self.assertRaises(TypeError):
      some_map["a"] = 17

  def test_persistent_get(self):
    some_map = LPCMSet(name = "some_map")
    another_map = LPCMSet(name = "another_map")
    some_map["a"] = ["123"]
    some_map["b"] = ["456"]
    some_map["c"] = [1, 2, 3, 4]
    some_map["d"] = set()
    another_map["a"] = ("it's a ", "sunny day")
    another_map["b"] = ("456", "789")
    another_map["c"] = [5, 6, 7, 8]
    another_map["d"] = set()
    try:
      self.assertEquals(some_map["a"], {"123"})
      self.assertEquals(some_map["b"], {"456"})
      self.assertEquals(some_map["c"], {1, 2, 3, 4})
      self.assertEquals(some_map["d"], set())
      self.assertEquals(another_map["a"], {"it's a ", "sunny day"})
      self.assertEquals(another_map["b"], {"456","789"})
      self.assertEquals(another_map["c"], {5, 6, 7, 8})
      self.assertEquals(another_map["d"], set())
      cache.clear()
      self.assertEquals(some_map["a"], {"123"})
      self.assertEquals(some_map["b"], {"456"})
      self.assertEquals(some_map["c"], {1, 2, 3, 4})
      self.assertEquals(some_map["d"], set())
      self.assertEquals(another_map["a"], {"it's a ", "sunny day"})
      self.assertEquals(another_map["b"], {"456","789"})
      self.assertEquals(another_map["c"], {5, 6, 7, 8})
      self.assertEquals(another_map["d"], set())
    finally:
      some_map.delete("a")
      some_map.delete("b")
      some_map.delete("c")
      some_map.delete("d")
      another_map.delete("a")
      another_map.delete("b")
      another_map.delete("c")
      another_map.delete("d")
    with self.assertRaises(KeyError):
      a = some_map["bad_key"]

  def test_insert_values(self):
    some_map = LPCMSet(name = "some_map")
    some_map["some_list"] = [1,2,3,4]
    some_map.insert_values("some_list", [5,6,7])
    some_map.insert_values("some_list", [8,9,10])
    some_map.insert_values("other_list", [11, 12, 13])
    cache.clear()
    try:
      self.assertEquals(some_map["some_list"], {1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
      self.assertEquals(some_map["other_list"], {11, 12, 13})
    finally:
      some_map.delete("some_list")
      some_map.delete("other_list")

class TestLCMSet(LPCMTestCase):

  def setUp(self):
    super(TestLCMSet, self).setUp()
    cache.clear()

  def test_value_must_be_set(self):
    some_map = LCMSet(name = "some_map")
    with self.assertRaises(TypeError):
      some_map["a"] = 17

  def test_simple_get(self):
    some_map = LCMSet(name = "some_map")
    another_map = LCMSet(name = "another_map")
    some_map["a"] = ["123"]
    some_map["b"] = ["456"]
    some_map["c"] = [1,2,3,4]
    some_map["d"] = []
    another_map["a"] = ("it's a ", "sunny day")
    another_map["b"] = ("456", "789")
    another_map["c"] = [5, 6, 7, 8]
    another_map["d"] = set()
    self.assertEquals(some_map["a"], {"123"})
    self.assertEquals(some_map["b"], {"456"})
    self.assertEquals(some_map["c"], {1, 2, 3, 4})
    self.assertEquals(some_map["d"], set())
    self.assertEquals(another_map["a"], {"it's a ", "sunny day"})
    self.assertEquals(another_map["b"], {"456","789"})
    self.assertEquals(another_map["c"], {5, 6, 7, 8})
    self.assertEquals(another_map["d"], set())
    cache.clear()
    with self.assertRaises(KeyError):
      _ = some_map["a"]

  def test_insert_values(self):
    some_map = LCMSet(name = "some_map")
    some_map["some_list"] = [1,2,3,4]
    some_map.insert_values("some_list", [5, 6, 7])
    some_map.insert_values("some_list", [7, 8, 9,10])
    some_map.insert_values("other_list", [10, 11, 12, 13])
    self.assertEquals(some_map["some_list"], {1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
    self.assertEquals(some_map["other_list"], {10, 11, 12, 13})
