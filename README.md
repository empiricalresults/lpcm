lpcm
====

Large Persistent Cached Map: A dictionary-like Django interface for Memcached and AWS DynamoDB

Requirements
------------
* Django 1.4
* pylibmc
* boto

Django is not really required for any of the `lpcm` core logic and is only used as
a convenient framework for accessing memcached and running unit tests.
If you require `lpcm` in a non-django Python project, please contact me and
I will help you set it up.

Running the Tests
-----------------
In `settings.py`, set your AWS credentials for `LPCM_DYNAMODB_ACCESS_KEY`
and `LPCM_DYNAMODB_SECRET_ACCESS_KEY`.
Then run: 
`manage.py test lpcm`

Adding lpcm to your own projects
--------------------------------
Simply copy the `lpcm` directory (inside `project`) and add the required fields to
your setttings module. Remember to also add it to your `INSTALLED_APPS`.
