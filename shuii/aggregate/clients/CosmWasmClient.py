# https://github.com/cosmos/chain-registry
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.contract import LedgerContract

configs = {
    'juno-1': {
        "url": "rest+https://lcd.junomint.com",
        "fee_minimum_gas_price": 0.0025,
        "fee_denomination": "ujuno",
        "staking_denomination": "ujuno",
    }
}

# cfg = NetworkConfig(
#     chain_id="juno-1",
#     url="rest+https://lcd.junomint.com",
#     fee_minimum_gas_price=0.0025,
#     fee_denomination="ujuno",
#     staking_denomination="ujuno",
# )

# ledger = LedgerClient(cfg)

# balance = ledger.query_bank_balance(
#     'juno14l0euhdndthtynfhkf74qpnlw45pfy6k0lktkn')

# print(balance)

# contract = LedgerContract(
#     path=None, client=ledger, address="juno1e229el8t4lu4rx7xeekc77zspxa2gz732ld0e6a5q0sr0l3gm78stuvc5g")

# `owner_of`, `approval`, `approvals`, `all_operators`, `num_tokens`, `contract_info`, `nft_info`, `all_nft_info`, `tokens`, `all_tokens`, `minter`
# print(contract.query({
#     'contract_info': {},
# }))

# print(contract.query({
#     'all_tokens': {}
# }))

# print(contract.query({
#     'all_nft_info': {}
# }))

# print(contract.query({
#     'nft_info': {
#         'token_id': 'JunoPunks.8'
#     }
# }))


class CosmWasmClient:
    def __init__(self, chain_id):
        config = configs[chain_id]
        self.ledger = LedgerClient(
            NetworkConfig(
                chain_id=chain_id,
                url=config['url'],
                fee_minimum_gas_price=config['url'],
                fee_denomination=config['fee_denomination'],
                staking_denomination=config['staking_denomination'],
            )
        )

    def query(self, address):
        try:
            contract = LedgerContract(
                path=None, client=self.ledger, address=address)

            contract_info = contract.query({
                'contract_info': {},
            })

            token = contract.query({
                'all_tokens': {
                    'limit': 1
                }
            })['tokens'][0]

            token_metadata = contract.query({
                'nft_info': {
                    'token_id': token
                }
            })

            return {
                'address': address,
                'name': contract_info['name'],
                'symbol': contract_info['symbol'],
                'token_uri': self.standardize_uri(token_metadata['token_uri']),
                'starting_index': token[-1],
                'total_supply': '0',
                'suffix': None
            }
        except:
            raise Exception("Something broke whoops")

    def standardize_uri(self, uri):
        if uri[len(uri) - 5:] == '.json':
            #uri = uri[:-5]
            uri = uri.split('/')
            uri = '/'.join(uri[:-1])
            return uri + '/_metadata.json'

        raise Exception("CosmWasmClient: Unexpected URI format")


# client = CosmWasmClient('juno-1')
# print(client.query('juno1e229el8t4lu4rx7xeekc77zspxa2gz732ld0e6a5q0sr0l3gm78stuvc5g'))
