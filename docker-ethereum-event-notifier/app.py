# import the following dependencies
import json
import boto3
import os
import requests
from web3 import Web3
import asyncio
import logging
from pythonjsonlogger import jsonlogger

class EthereumContractNotifier():

    def __init__(self,
                 node_url,
                 contract_address,
                 poll_interval=10):
        self.contract_address = contract_address
        self.node_url = node_url
        self.poll_interval = poll_interval
        
        self._setup_logging()
        self._setup_connection()
        self._setup_contract()
        self._setup_filters()
        self._setup_event_bus()
        
        self.logger.info('contract_address:{}'.format(self.contract_address))
        self.logger.info('node_url:{}'.format(self.node_url))
        self.logger.info('is_connected:{}'.format(self.w3.isConnected()))
        self.logger.info('event_names:{}'.format(list(self.event_filters.keys())))

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(logHandler)

    def _setup_connection(self):
        self.w3 = Web3(Web3.HTTPProvider(self.node_url))

    def _setup_contract(self):
        abi_url = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}'.format(self.contract_address)
        abi_result = requests.get(abi_url).json()
        self.contract_abi = json.loads(abi_result['result'])
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
    
    def _setup_filters(self):
        self.event_filters = {}
        event_names = [v['name']  for v in self.contract_abi if v['type'] == 'event']
        for event_name in event_names:
            self.event_filters[event_name] = self.contract.events[event_name].createFilter(fromBlock='latest')

    def _setup_event_bus(self):
        self.client = boto3.client('events')
        self.event_bus_name = 'ethereum_contract_events'
        try:
            self.client.create_event_bus(Name=self.event_bus_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def handle_event(self, event):
        detail = json.loads(Web3.toJSON(event), parse_int=str)
        response = self.client.put_events(
            Entries=[{
                'DetailType': 'Ethereum contract event notifications',
                'Detail': json.dumps(detail),
                'EventBusName': self.event_bus_name,
                'Source': 'ethereum'}
            ]
        )
        # No error handling
        logging.info(detail)
        logging.info(response)

    async def gather_event(self, event_filter_name, event_filter):
        logging.debug('gather_event: event_filter_name:{}'.format(event_filter_name))
        try:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
        except ValueError as e:
            logging.error(e)

    async def gather_events(self, poll_interval):
        logging.debug('gather_events: poll_interval:{}'.format(poll_interval))
        while True:
            coroutines = [self.gather_event(event_filter_name, event_filter)
                      for event_filter_name, event_filter in self.event_filters.items()]
            asyncio.gather(*coroutines)
            await asyncio.sleep(poll_interval)
    
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.gather_events(poll_interval=self.poll_interval))
        finally:
            loop.close()

if __name__ == "__main__":
    notifier = EthereumContractNotifier(
        node_url=os.environ.get('NODE_URL'),
        contract_address=os.environ.get('CONTRACT_ADDRESS'),
        poll_interval=os.environ.get('POLL_INTERVAL', 10))
    notifier.run()
