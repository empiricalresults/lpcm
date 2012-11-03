# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from django.core.cache import cache
from base import LPCMTestCase
from ..lcm import LargeCachedMap as LCM

class TestLCM(LPCMTestCase):

  def setUp(self):
    super(TestLCM, self).setUp()
    cache.clear()

  def test_simple_get(self):
    some_map = LCM(name = "some_map")
    another_map = LCM(name = "another_map")
    some_map["a"] = 123
    some_map["b"] = "some string"
    some_map["c"] = 7.890
    another_map["a"] = 234
    another_map["b"] = "another string"
    another_map["c"] = 8.901
    self.assertEquals(some_map["a"], 123)
    self.assertEquals(some_map["b"], "some string")
    self.assertEquals(some_map["c"], 7.890)
    self.assertEquals(another_map["a"], 234)
    self.assertEquals(another_map["b"], "another string")
    self.assertEquals(another_map["c"], 8.901)
    cache.clear()
    with self.assertRaises(KeyError):
      a = some_map["a"]

  def test_contains(self):
    some_map = LCM(name = "some_map")
    some_map["a"] = 123
    self.assertIn('a', some_map)
    self.assertNotIn('bad_key', some_map)

  def test_delete(self):
    some_map = LCM(name = "some_map")
    some_map["a"] = 123
    self.assertEquals(some_map["a"], 123)
    some_map.delete("a")
    with self.assertRaises(KeyError):
      a = some_map["a"]
    some_map.delete("lala_i_don't_exist") # deleting non existent key is fine

  def test_get(self):
    some_map = LCM(name = "some_map")
    some_map["a"] = 123
    self.assertEquals(some_map.get("a", 234), 123)
    self.assertEquals(some_map.get("bad_key", 234), 234)

  def test_unicode(self):
    some_map = LCM(name = "some_map")
    unicode_key = 'Ivan Krsti\xc4\x87'.decode('utf8')
    unicode_value = 'Ivan Krsti\xc4\x87 is unicode'.decode('utf8')
    some_map[unicode_key] = unicode_value
    self.assertEquals(some_map[unicode_key], unicode_value)


  def test_increment(self):
    some_map = LCM(name = "some_map")
    some_map['a'] = 41
    some_map.increment('a')
    self.assertEquals(some_map['a'], 42)
    some_map.increment('a', 4.2)
    self.assertEquals(some_map['a'], 46.2)

  def test_decrement(self):
    some_map = LCM(name = "some_map")
    some_map['a'] = 43
    some_map.decrement('a')
    self.assertEquals(some_map['a'], 42)
    some_map.decrement('a', 1.9)
    self.assertEquals(some_map['a'], 40.1)
    some_map.decrement('a', 50.1)
    self.assertEquals(some_map['a'], -10)

  def test_increment_non_existent(self):
    some_map = LCM(name = "some_map")
    some_map.increment('new_key')
    self.assertEquals(some_map['new_key'], 1)
    some_map.increment('another_key', 10)
    self.assertEquals(some_map['another_key'], 10)

  def test_bad_increment(self):
    some_map = LCM(name = "some_map")
    some_map['a'] = 41
    with self.assertRaises(ValueError):
      some_map.increment('a', 'bcde')

