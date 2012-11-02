# Copyright (c) 2012 Yavar Naddaf http://www.empiricalresults.ca/
# Released Under GNU General Public License. www.gnu.org/licenses/gpl-3.0.txt


import logging
from django.core.management.base import BaseCommand
from ...dynamodb import DynamoDB
from ... import config

class Command(BaseCommand):
  help = """ Creates the DynamoDB table used by LPCM"""

  def handle(self, *args, **options):
    num_created = 0
    table_name = config.LPCM_DYNAMODB_TABLE_NAME
    conn = DynamoDB.get_connection()
    tables = conn.list_tables()
    if table_name in tables:
      logging.warning("LPCM table already exists and will not be recreated.")
      return
    table = DynamoDB.create_table(table_name,
      hash_key_name = 'table',
      hash_key_proto_value = 'S',
      range_key_name = 'key',
      range_key_proto_value = 'S',
      read_units = config.LPCM_PROVISIONED_THROUGHPUT['read_units'],
      write_units = config.LPCM_PROVISIONED_THROUGHPUT['write_units'],
      )
    if table:
      logging.info("Successfully created table {}.".format(table_name))
    else:
      logging.error("Unable to create table {}.".format(table_name))
