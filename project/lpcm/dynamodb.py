# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt

from collections import namedtuple
import boto
from thread_local import lpcm_thread_local
import config

DynamoDBKey = namedtuple('DynamoDBKey',
  field_names = ['hash_key', 'range_key', 'cache_key', 'original_key_obj'])

class DynamoDB(object):

  @classmethod
  def get_connection(cls):
    "Returns a thread-local dynamodb-boto connection"
    try:
      return lpcm_thread_local.ddb_connection
    except AttributeError:
      pass
    lpcm_thread_local.ddb_connection = boto.connect_dynamodb(
      config.DYNAMODB_ACCESS_KEY,
      config.DYNAMODB_SECRET_ACCESS_KEY)
    return lpcm_thread_local.ddb_connection

  @classmethod
  def get_table(cls, table_name):
    "Note that tables are cached by trhead"
    if table_name in lpcm_thread_local.ddb_table_cache:
      return lpcm_thread_local.ddb_table_cache[table_name]
    conn = cls.get_connection()
    tables = conn.list_tables()
    if table_name not in tables:
      raise cls.TableNotFound("Table {} not found".format(table_name))
    lpcm_thread_local.ddb_table_cache[table_name] = conn.get_table(table_name)
    return lpcm_thread_local.ddb_table_cache[table_name]

  @classmethod
  def get_item(cls, ddb_key):
    "Tries to get an item from DynamoDB. Throws DynamoDBKeyNotFoundError"
    table = cls.get_table(config.LPCM_DYNAMODB_TABLE_NAME)
    return table.get_item(hash_key = ddb_key.hash_key, range_key = ddb_key.range_key)

  @classmethod
  def create_item(cls, ddb_key):
    table = DynamoDB.get_table(config.LPCM_DYNAMODB_TABLE_NAME)
    return table.new_item(hash_key = ddb_key.hash_key, range_key = ddb_key.range_key)

  @classmethod
  def create_table(cls, table_name, hash_key_name, hash_key_proto_value,
      range_key_name, range_key_proto_value, read_units, write_units):
    """ Creates a table in dynamo db.
    This probably shouldn't be called in production code.
    For a sample of table schema, see: http://boto.readthedocs.org/en/latest/dynamodb_tut.html
    """
    conn = cls.get_connection()
    schema = conn.create_schema(
      hash_key_name = hash_key_name,
      hash_key_proto_value = hash_key_proto_value,
      range_key_name = range_key_name,
      range_key_proto_value = range_key_proto_value)
    table = conn.create_table(
          name = table_name,
          schema = schema,
          read_units = read_units,
          write_units = write_units)
    return table

  class TableNotFound(KeyError):
    pass
