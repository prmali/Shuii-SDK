# CosmWasm721 Standard

import json
import asyncio
import aiohttp
import ssl
import certifi

from functools import cmp_to_key
import time
import os

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

limit = 0
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
        "token_id": decoded_res['edition'],
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


async def main(project_name, metadata_uri):
    global metadata, limit
    start_time = time.time()
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url=metadata_uri, ssl=SSL_CONTEXT) as response:
            res = await response.read()
            metadata = json.loads(res.decode("utf8"))
            limit = len(metadata)
            print(limit)

            await asyncio.gather(*[count(num) for num in range(limit)])

            for attributes in aggregate.values():
                for attribute in attributes.values():
                    composed.append(attribute)

            print("--- WEIGHING ---")
            await asyncio.gather(*[assign(attribute, limit) for attribute in composed])

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
    with open("%s.json" % (project_name.lower().replace(" ", "")), "w") as dumped:
        dumped.write(json.dumps({
            "project_name": project_name,
            "token_uri": metadata_uri,
            "limit": limit,
            "aggregate": aggregate,
            "weights": weights,
            "time_to_sync": finalized_time
        }))

    print("--- DONE ---")
    print("--- %s seconds ---" % (finalized_time))


def run(project_name, metadata_uri):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(project_name, metadata_uri))
    loop.close()


run("CwTest2 Issue2",
    "https://hopegalaxy.mypinata.cloud/ipfs/QmX1i7DKeHyDHrnhFT8ab4E5mtfgtGH4XQ29ETi3WsGS5a/_metadata.json")

print("INVALIDS:", invalids)
