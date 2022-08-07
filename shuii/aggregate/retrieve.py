import json
import argparse

parser = argparse.ArgumentParser(description='Rarity retriever')
parser.add_argument('--name', action="store",
                    dest='collection_name', default='')
parser.add_argument('--tokenid', action="store",
                    dest='token_id', default=0)
args = parser.parse_args()


def main(project_name, tokenId):
    f = json.load(open('%s.json' % (project_name)))
    for pos in range(len(f['weights'])):
        try:
            if f['weights'][pos]['token_id'] == tokenId:
                return f['weights'][pos]['rank'], f['weights'][pos]
        except:
            if f['weights'][pos]['tokenId'] == tokenId:
                return f['weights'][pos]['rank'], f['weights'][pos]


print(main(args.collection_name, int(args.token_id)))
#print(main("blankface", 3535))
