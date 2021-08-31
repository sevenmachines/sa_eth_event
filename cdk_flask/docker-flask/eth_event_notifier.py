# import the following dependencies
import json
import os
import requests
from web3 import Web3
import asyncio

class EthereumNotifier():

    def __init__(self, contract_address):
        self.contract_address = contract_address
        self.contract_abi = self._get_abi_from_contract_address(self.contract_address)
        self._setup_provider(event_name='PairCreated')

    def _setup_provider(self, event_name):
        if os.environ.get('WEB3_INFURA_PROJECT_ID', None):
            from web3.auto.infura import w3
            self.contract = w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
            event_signature_hash = w3.keccak(text="{}(uint32)".format(event_name)).hex()
            self.event_filter = w3.eth.filter({
                "address": self.contract_address,
                "topics": [event_signature_hash,
                   "0x000000000000000000000000000000000000000000000000000000000000000a"],
                })
            self.block_filter = w3.eth.filter('latest')
        else:
            return False
        return w3.isConnected()
          

    def _get_abi_from_contract_address(self, contract_address):
        abi_url = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}'.format(contract_address)
        abi_result = requests.get(abi_url).json()
        abi = json.loads(abi_result['result'])
        return abi
        
    def handle_event(self, event):
        import pdb; pdb.set_trace()
        print(event)

    async def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
                await asyncio.sleep(poll_interval)
    
    def main(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(self.block_filter, 2)))
        finally:
            loop.close()



if __name__ == "__main__":
    node_url = 'https://{}'.format(
        os.environ.get('node_address', 'mainnet.infura.io/v3/33036dd577fa4493a03d2d3ab1098676'))
    # uniswap address and abi
    uniswap_router = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    uniswap_factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    uniswap_factory_abi = json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')

    notifier = EthereumNotifier(contract_address=uniswap_router)
    notifier.main()