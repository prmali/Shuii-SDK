import json
import asyncio
import aiohttp
import ssl
import certifi
from functools import cmp_to_key

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

weights = []
aggregate = {}
invalids = []
composed = []


async def count(token_uri, token_id, session, suffix, retry_limit):
    for attempt in range(retry_limit):  # Until I can get around rate limits >:(
        try:
            async with session.get(url="%s/%s%s" % (token_uri, token_id, suffix), ssl=SSL_CONTEXT) as response:
                res = await response.read()
                decoded_res = json.loads(res.decode("utf8"))

                attributes = decoded_res["attributes"]

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

                #print("✅:", token_id)
                return
        except Exception as e:
            continue

    invalids.append(token_id)
    print("❌:", token_id)


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


async def main(project_name, token_uri, limit, starting_index=0, suffix="", retry_limit=500):
    async with aiohttp.ClientSession(trust_env=True) as session:
        print("===COUNTING===")
        await asyncio.gather(*[count(token_uri, num, session, suffix, retry_limit) for num in range(starting_index, starting_index + limit)])

        for attributes in aggregate.values():
            for attribute in attributes.values():
                composed.append(attribute)

        print("===WEIGHING===")
        await asyncio.gather(*[assign(attribute, limit) for attribute in composed])

        print("===SORTING===")
        weights.sort(key=cmp_to_key(compare), reverse=True)

    with open("%s.json" % (project_name.lower().replace(" ", "")), "w") as dumped:
        dumped.write(json.dumps({
            "project_name": project_name,
            "token_uri": token_uri,
            "limit": limit,
            "suffix": suffix,
            "starting_index": starting_index,
            "aggregate": aggregate,
            "weights": weights,
        }))

    print("===DONE===")

asyncio.run(main(
    "Doodles",
    "https://gateway.ipfs.io/ipfs/QmPMc4tcBsMqLRuCQtPmPe84bpSjrC3Ky7t3JWuHXYB4aS",
    limit=10000,
    starting_index=0,
    suffix='',
    retry_limit=500
))

print("INVALIDS:", invalids)