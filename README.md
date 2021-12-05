# Rarity Scanner

Aggregate metadata info on NFTs

Accuracy on par w/ legitimate tools afaik

### aggregate.py

#### description

Responsible for gathering info on collection, weighing rarities, and spitting into json file

#### how-to

Modify the main() function towards the bottom of the file (wrapped in asyncio's run method)

```py
asyncio.run(main(
    "NFT project",
    "https://gateway.ipfs.io/ipfs/some_hash",
    limit=10000,
    starting_index=0,
    suffix='',
    retry_limit=500
))
```

The `main` function takes in 6 parameters

1. Name of the NFT project
2. Base metadata uri of the tokens WITHOUT a trailing "/"
3. The maximum tokens which are part of the collection
4. The starting index of the collection, usually 0 or 1
5. Suffix of the metadata uri. Maybe the location ends in a ".json"
6. How many times should a request be repeated on a retrieval error before moving on to the next token

#### execute

```sh
python3 aggregate.py
```

### retrieve.py

#### description

Get the info on a specific token id.

#### how-to

No modification is needed. If you wish to hardcode the collection and tokenId values, uncomment out the last line

```py
#print(main("blankface", 3535))
```

The `main` function takes in 2 parameters

1. Name of the NFT project saved to a json file
2. The token ID you are looking to inspect

#### execute

```sh
python3 retrieve.py --name 'NFT project' --tokenid 3
```

### Whats left

-   Get rarity by rarity ID
-   Interface to visualize
-   _containerize_
-   improve efficiency
-   work around brute force retry method
