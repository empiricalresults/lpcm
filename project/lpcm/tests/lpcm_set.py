import unittest
from django.core.cache import cache
from base import LPCMTestCase
from .. import LPCMSet
from .. import config

class TestLPCMSet(LPCMTestCase):

  def setUp(self):
    super(TestLPCMSet, self).setUp()
    cache.clear()

  def test_value_must_be_set(self):
    regular_map = LPCMSet(name = "some_map", cache_only = False)
    with self.assertRaises(TypeError):
      regular_map["a"] = 17

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_non_cache_only(self):
    regular_map = LPCMSet(name = "some_map", cache_only = False)
    self.assertFalse(regular_map.cache_only)
    regular_map["a"] = ["123"]
    regular_map["b"] = ["456"]
    regular_map["c"] = [1,2,3,4]
    regular_map["d"] = set()
    try:
      self.assertEquals(regular_map["a"], set(["123"]))
      self.assertEquals(regular_map["b"], set(["456"]))
      self.assertEquals(regular_map["c"], set([1,2,3,4]))
      self.assertEquals(regular_map["d"], set())
      cache.clear()
      self.assertEquals(regular_map["a"], set(["123"]))
      self.assertEquals(regular_map["b"], set(["456"]))
      self.assertEquals(regular_map["c"], set([1,2,3,4]))
      self.assertEquals(regular_map["d"], set())
    finally:
      regular_map.delete("a")
      regular_map.delete("b")
      regular_map.delete("c")
      regular_map.delete("d")
    with self.assertRaises(KeyError):
      a = regular_map["bad_key"]

  def test_cache_only(self):
    cache_only_map = LPCMSet(name = "some_map", cache_only = True)
    self.assertTrue(cache_only_map.cache_only)
    cache_only_map["a"] = ["123"]
    cache_only_map["b"] = ["456"]
    cache_only_map["c"] = [1,2,3,4]
    cache_only_map["d"] = []
    self.assertEquals(cache_only_map["a"], set(["123"]))
    self.assertEquals(cache_only_map["b"], set(["456"]))
    self.assertEquals(cache_only_map["c"], set([1,2,3,4]))
    self.assertEquals(cache_only_map["d"], set())
    cache.clear()
    with self.assertRaises(KeyError):
      a = cache_only_map["a"]

  def test_insert_values_cache_only(self):
    cache_only_map = LPCMSet(name = "some_map", cache_only = True)
    cache_only_map["some_list"] = [1,2,3,4]
    cache_only_map.insert_values("some_list", [5, 6, 7])
    cache_only_map.insert_values("some_list", [7, 8, 9,10])
    cache_only_map.insert_values("other_list", [10, 11, 12, 13])
    self.assertEquals(cache_only_map["some_list"], set([1,2,3,4,5,6,7,8,9,10]))

  def test_insert_values_cache_only_non_existant(self):
    cache_only_map = LPCMSet(name = "some_map", cache_only = True)
    cache_only_map.insert_values("some_list", [5,6,7])
    cache_only_map.insert_values("some_list", [8,9,10])
    self.assertEquals(cache_only_map["some_list"], set([5,6,7,8,9,10]))

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_insert_values_non_cache_only(self):
    regular_map = LPCMSet(name = "some_map", cache_only = False)
    regular_map["some_list"] = [1,2,3,4]
    regular_map.insert_values("some_list", [5,6,7])
    regular_map.insert_values("some_list", [8,9,10])
    regular_map.insert_values("other_list", [11, 12, 13])
    cache.clear()
    try:
      self.assertEquals(regular_map["some_list"], set([1,2,3,4,5,6,7,8,9,10]))
    finally:
      regular_map.delete("some_list")

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_insert_values_non_cache_only_non_existant(self):
    regular_map = LPCMSet(name = "some_map", cache_only = False)
    regular_map.insert_values("some_list", [5,6,7])
    regular_map.insert_values("some_list", [8,9,10])
    cache.clear()
    try:
      self.assertEquals(regular_map["some_list"], set([5,6,7,8,9,10]))
    finally:
      regular_map.delete("some_list")
  
