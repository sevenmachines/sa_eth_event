# import the following dependencies
import json
import os
import requests
from web3 import Web3
import asyncio

class EthereumNotifier():

    def __init__(self, contract_address, event_name):
        self.contract_address = contract_address
        self.contract_abi = self._get_abi_from_contract_address(self.contract_address)
        self.w3 = None
        self._connect(provider='infura')
        self._setup_provider(event_name=event_name)

    def _connect(self, provider='infura'):
        if self.w3 is None or not self.w3.isConnected():
            from web3 import Web3
            if provider == 'infura':
                print('Connecting to Infura node')
                self.w3 = Web3(Web3.WebsocketProvider(
                    "wss://mainnet.infura.io/ws/v3/{}".format(os.environ.get('WEB3_INFURA_PROJECT_ID')), websocket_timeout=3600))
            elif provider == 'getblock':
                print('Connecting to GetBlock node')
                api_key = os.environ.get('GETBLOCK_API_KEY')
                self.w3 = Web3(Web3.WebsocketProvider("wss://eth.getblock.io/mainnet/?api_key={}".format(api_key), websocket_timeout=3600))
    
    def _setup_provider(self, event_name):
        print('Setting up filters...')
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        self.event_filter = self.contract.events[event_name].createFilter(fromBlock='latest')
        #self.block_filter = self.w3.eth.filter('latest')
        #self.transaction_filter = self.w3.eth.filter('pending')
    
    def _get_abi_from_contract_address(self, contract_address):
        abi_url = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}'.format(contract_address)
        abi_result = requests.get(abi_url).json()
        abi = json.loads(abi_result['result'])
        return abi
        
    def parse_event(self, event):
        event_abi = self.contract_abi[event['transactionIndex']]
        event_name = event_abi["name"]
        print(event_name)
        
    def handle_event(self, event):
        print(event)

    async def log_loop(self, event_filter, poll_interval):
        while True:
            try:
                for event in event_filter.get_new_entries():
                    print('Handling event...')
                    self.handle_event(event)
                    await asyncio.sleep(poll_interval)
            except ValueError:
                import pdb; pdb.set_trace()
                pass
    
    def main(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(self.event_filter , 2)
            ))
        finally:
            loop.close()



if __name__ == "__main__":
    apepunk_address = '0x97F2EEd9A7D3edBbca56120ED26795a5467f57fC'
    apepunk_event_name = 'CreatePunk'
    cryptopunk_address = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
    cryptopunk_event_name = 'PunkOffered'
    uniswap_router = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    uniswap_factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    uniswap_factory_abi = json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')

    notifier = EthereumNotifier(contract_address=cryptopunk_address, event_name=cryptopunk_event_name)
    notifier.main()
