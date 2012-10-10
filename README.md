lpcm
====

Large Persistent Cached Map: A dictionary-like Django interface for Memcached and AWS DynamoDB

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
