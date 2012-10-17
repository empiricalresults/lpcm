lpcm
====

Large Persistent Cached Map: a dictionary-like Django interface for AWS DynamoDB and memcached 

*lpcm* allows you to have a dictionary-like object in python that automatically interfaces
[DynamoDB](http://aws.amazon.com/dynamodb/) and [memcached](http://memcached.org/):

```python
  some_dict = LPCM('some_dict')
  some_dict['pi'] = 3.1415
```

This will save a key-value pair ``pi: 3.1415`` in both memcached and DynamoDB associated with
the map name ``some_dict``. Similarly, you can access the stored values like a
regular dictionary:

```python
  some_dict = LPCM('some_dict')
  try:
    v = some_dict['pi']
  except KeyError:
    print "The pi is a lie"
```

This will first look for the key ``pi`` associated with the map name ``some_dict``
in memcached. If no associated value is found in
memcached, a query is sent to DynamoDB. If DynamoDB returns a value, it will be cached in memcached and then returned, otherwise
a ``KeyError`` exception is raised.

Atomic increments are also supported:

```python
  user_count = LPCM('user_count')
  user_count[request.user.id].increment()
```

In addition to the syntactic sugar, *lpcm* allows you insulate your production data
from the data accessed by unittests and general development.  It also allows you to get
faster and cheaper testing by switching to cached-only testing during development.

A detailed discussion of the motivations and use cases for *lpcm* is provided [here](http://www.empiricalresults.ca/blog/2012/10/16/lpcm:-large-persistent-cached-map.-a-dictionary-like-django-interface-for-memcached-and-dynamodb/).

Requirements
------------
* Python 2.7+
* Django 1.4+
* pylibmc
* boto

Django is not really required for any of the `lpcm` core logic and is only used as
a convenient framework for accessing memcached and running unit tests.
If you require `lpcm` in a non-django Python project, please contact me and
I will help you set it up.

Running the Tests
-----------------
1. In `settings.py`, set your AWS credentials for `LPCM_DYNAMODB_ACCESS_KEY`
and `LPCM_DYNAMODB_SECRET_ACCESS_KEY`.
2. You can either create the DynamoDB table (by default called`lpcm`) manually through the AWS console, or run
`manage.py create_lpcm_table`
3. Run the tests:
`manage.py test lpcm`

Adding lpcm to your own projects
--------------------------------
Simply copy the `lpcm` directory (inside `project`) and add the required fields to
your settings module. Remember to also add it to your `INSTALLED_APPS`.


License
-------
Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For a copy of the GNU General Public License, please see:
<http://www.gnu.org/licenses/>.
