# CosmWasm721 Standard

import json
import asyncio
import aiohttp
import ssl
import certifi

from functools import cmp_to_key
import time
import os

from shuii.aggregate.clients import CosmWasmClient
from shuii.aggregate.indexers import SingleDocument, MultiDocument

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

metadata = []
weights = []
aggregate = {}
invalids = []
composed = []


async def count(token_id):
    decoded_res = metadata[token_id]
    attributes = decoded_res["attributes"]

    attributes.append({
        'trait_type': 'num_traits',
        'value': len([attrib for attrib in attributes if attrib['value']])
    })

    weights.append({
        "token_id": decoded_res['edition'] or token_id,
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

    """invalids.append(token_id)
    print("❌:", token_id)"""


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


# detect project name
async def main(address, chain):
    global metadata
    start_time = time.time()
    cwClient = CosmWasmClient(chain)
    collection_metadata = cwClient.getCollectionMetadata(address)

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url=collection_metadata['token_uri'], ssl=SSL_CONTEXT) as response:
            res = await response.read()
            metadata = json.loads(res.decode("utf8"))
            collection_metadata['total_supply'] = len(metadata)
            collection_metadata['name'] = ' '.join(
                metadata[0]['name'].split(' ')[:-1])
            collection_metadata['symbol'] = ''.join(
                s[0] for s in collection_metadata['name'].split(' '))

            print("--- COUNTING ---")
            await asyncio.gather(*[count(num) for num in range(collection_metadata['total_supply'])])

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

    finalized_time = time.time() - start_time
    with open("%s.json" % (collection_metadata['name'].lower().replace(" ", "")), "w") as dumped:
        dumped.write(json.dumps({
            'network': chain.upper(),
            'address': collection_metadata['address'],
            'project_name': collection_metadata['name'],
            'project_symbol': collection_metadata['symbol'],
            'token_uri': collection_metadata['token_uri'],
            'total_supply': collection_metadata['total_supply'],
            'suffix': collection_metadata['suffix'],
            'starting_index': collection_metadata['starting_index'],
            'time_to_sync': finalized_time,
            'aggregate': aggregate,
            'weights': weights,
        }))

    print("--- DONE ---")
    print("--- %s seconds ---" % (finalized_time))


def run(address, chain):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(address, chain))
    loop.close()


#run('juno1e229el8t4lu4rx7xeekc77zspxa2gz732ld0e6a5q0sr0l3gm78stuvc5g', 'juno-1')
#print("INVALIDS:", invalids)
