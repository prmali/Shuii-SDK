import os
import json
from web3 import Web3

erc721abi = [
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_tokenId", "type": "uint256"}
        ],
        "name": "tokenURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


class EthereumClient:
    def __init__(self, ALCHEMY_API_KEY):
        self.abi = erc721abi
        self.w3 = Web3(Web3.HTTPProvider(
            f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'))

    def getCollectionMetadata(self, address):
        try:
            address = Web3.toChecksumAddress(address)
            contract = self.w3.eth.contract(address, abi=self.abi)
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            total_supply = contract.functions.totalSupply().call()
            token_uri = None
            starting_index = 0
            suffix = ''

            try:
                token_uri = contract.functions.tokenURI(0).call()
                starting_index = 0
            except:
                token_uri = contract.functions.tokenURI(1).call()
                starting_index = 1

            if token_uri[len(token_uri) - 5:] == '.json':
                suffix = '.json'
                token_uri = token_uri[:-5]

            token_uri = token_uri[:-2]

            return {
                'address': address,
                'name': name,
                'symbol': symbol,
                'token_uri': token_uri,
                'starting_index': starting_index,
                'total_supply': total_supply,
                'suffix': suffix,
            }
        except:
            raise Exception("Unable to get collection metadata. Whoopsies")
