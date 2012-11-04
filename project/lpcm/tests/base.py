# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from django.test import TestCase
from ..thread_local import set_in_test

class LPCMTestCase(TestCase):
  def __init__(self, *args, **kwargs):
    super(LPCMTestCase, self).__init__(*args, **kwargs)
    set_in_test()

  def _fixture_teardown(self):
    super(LPCMTestCase, self)._fixture_teardown()
    from ..cleanup import LPCMCleanUp
    LPCMCleanUp.full_clean_up()