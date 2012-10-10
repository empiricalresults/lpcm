import unittest
from django.core.cache import cache
from base import LPCMTestCase
from .. import LPCM
from .. import config

class TestLPCM(LPCMTestCase):

  def setUp(self):
    super(TestLPCM, self).setUp()
    cache.clear()

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_non_cache_only(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    self.assertFalse(regular_map.cache_only)
    regular_map["a"] = 123
    regular_map["b"] = "some string"
    regular_map["c"] = 7.890
    try:
      self.assertEquals(regular_map["a"], 123)
      self.assertEquals(regular_map["b"], "some string")
      self.assertEquals(regular_map["c"], 7.890)
    finally:
      regular_map.delete("a")
      regular_map.delete("b")
      regular_map.delete("c")
    with self.assertRaises(KeyError):
      a = regular_map["bad_key"]

  def test_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    self.assertTrue(cache_only_map.cache_only)
    cache_only_map["a"] = 123
    cache_only_map["b"] = "some string"
    cache_only_map["c"] = 7.890
    self.assertEquals(cache_only_map["a"], 123)
    self.assertEquals(cache_only_map["b"], "some string")
    self.assertEquals(cache_only_map["c"], 7.890)
    cache.clear()
    with self.assertRaises(KeyError):
      a = cache_only_map["a"]

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_presistent(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    regular_map["a"] = 123
    regular_map["b"] = "some string"
    regular_map["c"] = 7.890
    cache.clear()
    try:
      self.assertEquals(regular_map["a"], 123)
      self.assertEquals(regular_map["b"], "some string")
      self.assertEquals(regular_map["c"], 7.890)
    finally:
      regular_map.delete("a")
      regular_map.delete("b")
      regular_map.delete("c")
      regular_map.delete("d")

  def test_delete_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    cache_only_map["a"] = 123
    self.assertEquals(cache_only_map["a"], 123)
    cache_only_map.delete("a")
    with self.assertRaises(KeyError):
      a = cache_only_map["a"]
    # deleting non existant key should be fine
    cache_only_map.delete("lala_i_don't_exist")

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_delete_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    regular_map["a"] = 123
    self.assertEquals(regular_map["a"], 123)
    regular_map.delete("a")
    with self.assertRaises(KeyError):
      a = regular_map["a"]
    # deleting non existant key should be fine
    regular_map.delete("lala_i_don't_exist")

  def test_unicode_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    unicode_value = 'Ivan Krsti\xc4\x87 is unicode'.decode('utf8')
    cache_only_map[unicode_key] = unicode_value
    self.assertEquals(cache_only_map[unicode_key], unicode_value)


  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_unicode_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    unicode_value = 'Ivan Krsti\xc4\x87 is unicode'.decode('utf8')
    try:
      regular_map[unicode_key] = unicode_value
      self.assertEquals(regular_map[unicode_key], unicode_value)
    finally:
      regular_map.delete(unicode_key)

  def test_increment_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    cache_only_map['a'] = 41
    cache_only_map.increment('a')
    self.assertEquals(cache_only_map['a'], 42)
    cache_only_map.increment('a', 4.2)
    self.assertEquals(cache_only_map['a'], 46.2)

  def test_decrement_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    cache_only_map['a'] = 43
    cache_only_map.decrement('a')
    self.assertEquals(cache_only_map['a'], 42)
    cache_only_map.decrement('a', 1.9)
    self.assertEquals(cache_only_map['a'], 40.1)
    cache_only_map.decrement('a', 50.1)
    self.assertEquals(cache_only_map['a'], -10)

  def test_increment_non_existant_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    cache_only_map.increment('new_key')
    self.assertEquals(cache_only_map['new_key'], 1)
    cache_only_map.increment('another_key', 10)
    self.assertEquals(cache_only_map['another_key'], 10)

  def test_bad_incrementy_cache_only(self):
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    cache_only_map['a'] = 41
    with self.assertRaises(ValueError):
      cache_only_map.increment('a', 'bcde')

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_increment_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    try:
      regular_map['a'] = 41
      regular_map.increment('a')
      self.assertEquals(regular_map['a'], 42)
      regular_map.increment('a', 4.2)
      self.assertEquals(regular_map['a'], 46.2)
    finally:
      regular_map.delete('a')

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_increment_non_existant_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    try:
      regular_map.increment('new_key')
      self.assertEquals(regular_map['new_key'], 1)
      regular_map.increment('another_key', 10)
      self.assertEquals(regular_map['another_key'], 10)
    finally:
      regular_map.delete('new_key')
      regular_map.delete('another_key')

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_bad_incrementy_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    try:
      with self.assertRaises(ValueError):
        regular_map.increment('new_key', 'bcde')
    finally:
      regular_map.delete('new_key')

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_decrement_regular(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    try:
      regular_map['a'] = 43
      regular_map.decrement('a')
      self.assertEquals(regular_map['a'], 42)
      regular_map.decrement('a', 1.9)
      self.assertEquals(regular_map['a'], 40.1)
      regular_map.decrement('a', 50.1)
      self.assertEquals(regular_map['a'], -10)
    finally:
      regular_map.delete('a')

  @unittest.skipIf(config.LPCM_TEST_USE_LOCAL_CACHE_ONLY, "Disable in CACHE_ONLY mode")
  def test_disable_caching(self):
    regular_map = LPCM(name = "some_map", cache_only = False)
    cache_only_map = LPCM(name = "some_map", cache_only = True)
    try:
      regular_map["a"] = 123
      cache_only_map.increment('a')
      self.assertEquals(regular_map['a'], 124)  # reads from the incremented cash
      regular_map.disable_caching()
      self.assertEquals(regular_map['a'], 123)  # reads from the untouched dynamodb
    finally:
      regular_map.delete("a")
