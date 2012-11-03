# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from  django import dispatch

class Signals(object):
  pre_update = dispatch.Signal(providing_args=["map_name", "key", "action"])
  post_update = dispatch.Signal(providing_args=["map_name", "key", "action"])
