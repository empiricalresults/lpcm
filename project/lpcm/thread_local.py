# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from threading import local

lpcm_thread_local = local()
lpcm_thread_local.is_in_test = False
lpcm_thread_local.ddb_table_cache = {}

def is_in_test():
  return lpcm_thread_local.is_in_test

def set_in_test():
  lpcm_thread_local.is_in_test = True
