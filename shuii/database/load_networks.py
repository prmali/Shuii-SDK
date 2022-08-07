import json
import sys
import os
from DatabaseClient import DatabaseClient

f = open(os.path.join(os.path.dirname(__file__), 'networks.json'))
networks = json.load(f)

client = DatabaseClient()
raw_data = []
command = ''

for network in networks:
    raw_data.append((network['name'], network['symbol']))

client.queue_command(client.prep_data(
    'networks', ('network_name', 'network_symbol'), tuple(raw_data)))
client.execute()
