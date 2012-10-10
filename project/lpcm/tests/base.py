from django.test import TestCase
from ..thread_local import set_in_test

class LPCMTestCase(TestCase):
  def __init__(self, *args, **kwargs):
    super(LPCMTestCase, self).__init__(*args, **kwargs)
    set_in_test()
