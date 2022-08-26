# EthereumRC721 Standard

import json
import asyncio
import aiohttp
import ssl
import certifi
import time
import os

from decouple import config
from functools import cmp_to_key
from shuii.aggregate.clients import EthereumClient
from shuii.aggregate.indexers import MultiDocument

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

weights = []
aggregate = {}
invalids = []
composed = []

proxies = ['socks5://192.111.129.145:16894',
           'socks5://67.201.33.10:25283',
           'socks5://98.162.25.23:4145']


async def count(token_id, metadata):
    attributes = metadata["attributes"]

    attributes.append({
        'trait_type': 'num_traits',
        'value': len([attrib for attrib in attributes if attrib['value']])
    })

    weights.append({
        "token_id": token_id,
        "attributes": attributes
    })

    for i in attributes:
        if not i["trait_type"] in aggregate:
            aggregate[i["trait_type"]] = {}

        if not i["value"] in aggregate[i["trait_type"]]:
            aggregate[i["trait_type"]][i["value"]] = {
                "count": 0,
                "weight": 0
            }

        aggregate[i["trait_type"]][i["value"]]["count"] += 1


async def assign(attribute, limit):
    attribute["weight"] = round(1 / (attribute["count"] / limit), 3)


def weigh(metadata):
    if "weight" in metadata.keys():
        return metadata["weight"]

    weight = 0
    for attribute in metadata["attributes"]:
        weight += aggregate[attribute["trait_type"]
                            ][attribute["value"]]["weight"]

    metadata["weight"] = weight
    return weight


def compare(a, b):
    return weigh(a) - weigh(b)


async def main(address, retry_limit=500):
    start_time = time.time()
    ALCHEMY_API_KEY = config('ALCHEMY_API_KEY')
    ethClient = EthereumClient(ALCHEMY_API_KEY)
    indexer = MultiDocument(retry_limit)
    collection_metadata = ethClient.getCollectionMetadata(address)
    token_uri = collection_metadata['token_uri'].replace(
        "ipfs://", "https://gateway.ipfs.io/ipfs/")
    suffix = collection_metadata['suffix']

    print("--- GATHER ---")
    await asyncio.gather(*[indexer.create_job(token_id, "%s/%s%s" % (token_uri, token_id, suffix)) for token_id in range(collection_metadata['starting_index'], collection_metadata['starting_index'] + collection_metadata['total_supply'])])
    await indexer.execute_jobs()

    print("--- COUNTING ---")
    await asyncio.gather(*[count(token_id, indexer.results[token_id]) for token_id in indexer.results])
    # await asyncio.gather(*[count(token_uri, num, session, suffix, retry_limit) for num in range(collection_metadata['starting_index'], collection_metadata['starting_index'] + collection_metadata['total_supply'])])

    for attributes in aggregate.values():
        for attribute in attributes.values():
            composed.append(attribute)

    print("--- WEIGHING ---")
    await asyncio.gather(*[assign(attribute, collection_metadata['total_supply']) for attribute in composed])

    print("--- SORTING ---")
    weights.sort(key=cmp_to_key(compare), reverse=True)

    print("--- RANKING ---")
    current_rank, prev_weight = 1, weights[0]['weight']
    for weightIndex in range(len(weights)):
        if weights[weightIndex]['weight'] != prev_weight:
            prev_weight = weights[weightIndex]['weight']
            current_rank += 1

        weights[weightIndex]['rank'] = current_rank

    finish_time = time.time()
    finalized_time = finish_time - start_time
    with open("%s.json" % (collection_metadata['name'].lower().replace(" ", "")), "w") as dumped:
        dumped.write(json.dumps({
            'network': "ETH",
            'address': collection_metadata['address'],
            'project_name': collection_metadata['name'],
            'project_symbol': collection_metadata['symbol'],
            'token_uri': token_uri,
            'total_supply': collection_metadata['total_supply'],
            'suffix': collection_metadata['suffix'],
            'starting_index': collection_metadata['starting_index'],
            'time_started': start_time,
            'time_finalized': finish_time,
            'time_to_sync': finalized_time,
            'aggregate': aggregate,
            'weights': weights,
        }))

    print("--- DONE ---")
    print("--- %s seconds ---" % (finalized_time))


def run(address, retry_limit):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(address, retry_limit))
    loop.close()


run("0x8a90cab2b38dba80c64b7734e58ee1db38b8992e", retry_limit=100)
#print("INVALIDS:", invalids)
