import psycopg2
import json
import sys
import os
import asyncio
import time
from config import config
from DatabaseClient import DatabaseClient

f = open(os.path.join(os.path.dirname(__file__),
                      '..', 'aggregate', 'data', 'doodles.json'))
aggregated_data = json.load(f)


def add_collection(client, data):
    client.queue_command(
        client.prep_data(
            'collections',
            (
                'network_id',
                'collection_address',
                'collection_name',
                'collection_symbol',
                'total_supply'
            ),
            data
        )
    )


async def add_traits(client, collection_id, data):
    traits = []

    async def iter_values(trait_type, value):
        traits.append(
            (
                collection_id,
                trait_type,
                value,
                data[trait_type][value]['count'],
                data[trait_type][value]['weight']
            )
        )

    async def iter_traits(trait_type):
        await asyncio.gather(*[iter_values(trait_type, value)
                               for value in data[trait_type]])

    await asyncio.gather(*[iter_traits(trait_type) for trait_type in data])

    client.queue_command(
        client.prep_data(
            'traits',
            (
                'collection_id',
                'trait_type',
                'value',
                'count',
                'weight',
            ),
            traits
        )
    )


def add_tokens(client, collection_id, data):
    tokens = []
    for rank in range(len(data)):
        tokens.append((
            collection_id,
            data[rank]['token_id'],
            rank,
            data[rank]['weight']
        ))

    client.queue_command(
        client.prep_data(
            'tokens',
            (
                'collection_id',
                'id',
                'rank',
                'weight'
            ),
            tokens
        )
    )


async def add_attributes(client, collection_id, data):
    cached_attributes = {}
    attributes = []

    async def iter_attributes(token_id, trait_type, value):
        trait_id = cached_attributes.get(
            (trait_type, value), None)

        if not trait_id:
            trait_id = client.query(
                f'SELECT trait_id from traits WHERE collection_id = {collection_id} AND trait_type = \'{trait_type}\' AND value = \'{value}\''
            )[0][0]
            cached_attributes[(trait_type, value)] = trait_id

        attributes.append(
            (
                collection_id,
                token_id,
                trait_id
            )
        )

    async def iter_ranks(rank):
        token_id = client.query(
            f'SELECT token_id from tokens WHERE collection_id = {collection_id} AND rank = {rank} AND id = {data[rank]["token_id"]}'
        )[0][0]

        await asyncio.gather(*[iter_attributes(token_id, attribute['trait_type'], attribute['value'])
                               for attribute in data[rank]['attributes']])

    await asyncio.gather(*[iter_ranks(rank) for rank in range(len(data))])

    client.queue_command(
        client.prep_data(
            'attributes',
            (
                'collection_id',
                'token_id',
                'trait_id',
            ),
            attributes
        )
    )


async def main(data):
    start_time = time.time()
    client = DatabaseClient()
    network_symbol = data['network']
    network_id = client.query(
        f'SELECT network_id from networks WHERE network_symbol = \'{network_symbol}\';')[0][0]

    collection_data = [
        network_id,
        data['address'],
        data['project_name'],
        data['project_symbol'],
        data['total_supply']
    ]
    add_collection(client, (tuple(collection_data),))
    client.execute()
    print("added collection")

    collection_id = client.query(
        f'SELECT collection_id from collections WHERE network_id = \'{network_id}\' AND collection_address = \'{data["address"]}\''
    )[0][0]

    await add_traits(client, collection_id, data['aggregate'])
    client.execute()
    print("added traits")

    add_tokens(client, collection_id, data['weights'])
    client.execute()
    print("added tokens")

    await add_attributes(client, collection_id, data['weights'])
    client.execute()
    print("added attributes")
    print(time.time() - start_time)


asyncio.run(main(aggregated_data))
