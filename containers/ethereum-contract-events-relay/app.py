# import the following dependencies
import json
import boto3
import os
import requests
from web3 import Web3
import asyncio
import logging


class EthereumContractNotifier():

    def __init__(self,
                 node_url,
                 contract_address,
                 poll_interval=10):
        """Initialise an EthereumContractNotifier

        Parameters
        ----------
        node_url : str
            The URL of the Web3 node
        contract_address : str
            The address of the contract to monitor
        poll_interval : int, optional
            The number of seconds to wait between polling for event changes
        """
        self.contract_address = contract_address
        self.node_url = node_url
        self.poll_interval = poll_interval
        
        self._setup_connection()
        self._setup_contract()
        self._setup_filters()
        self._setup_event_bus()
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        msg_data = {"contract_address": self.contract_address,
                    "node_url": self.node_url,
                    "is_connected": self.w3.isConnected(),
                    "event_names": list(self.event_filters.keys())}
        logging.info(json.dumps(msg_data))

    def _setup_connection(self):
        """
        Initialise the Web3 provider
        """
        self.w3 = Web3(Web3.HTTPProvider(self.node_url))

    def _setup_contract(self):
        """
        Initialise the Web3 contract and ABI data from EtherScan
        """
        abi_url = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}'.format(self.contract_address)
        abi_result = requests.get(abi_url).json()
        self.contract_abi = json.loads(abi_result['result'])
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
    
    def _setup_filters(self):
        """
        Initialise the Web3 filters. A filter specific to an event name will be
        create for all ABI-defined events on the contract.
        """
        self.event_filters = {}
        event_names = [v['name']  for v in self.contract_abi if v['type'] == 'event']
        for event_name in event_names:
            self.event_filters[event_name] = self.contract.events[event_name].createFilter(fromBlock='latest')

    def _setup_event_bus(self):
        """
        Create an Amazon EventBridge event bus if not existing already
        """
        self.client = boto3.client('events')
        self.event_bus_name = 'ethereum_contract_events'
        try:
            self.client.create_event_bus(Name=self.event_bus_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def handle_event(self, event):
        """
        Parse an event on a contract, translate into safe JSON and put onto
        the event bus
        """
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
        """
        Collect all new events on a contract that pass the event filter and send 
        for handling.
        """
        try:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
        except ValueError as e:
            logging.error(e)

    async def gather_events(self, poll_interval):
        """
        Concurrently poll each contract event type each given poll interval. 
        Only return if the Web3 connection to the provider is lost.
        """
        while self.w3.isConnected():
            coroutines = [self.gather_event(event_filter_name, event_filter)
                      for event_filter_name, event_filter in self.event_filters.items()]
            asyncio.gather(*coroutines)
            await asyncio.sleep(poll_interval)
    
    def run(self):
        """
        Gather all events and tidy up the system-loop on exit
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.gather_events(poll_interval=self.poll_interval))
        finally:
            loop.close()

if __name__ == "__main__":
    """
    Main entry point. Collect the required environment variables and start
    the main loop.
    """
    notifier = EthereumContractNotifier(
        node_url=os.environ.get('NODE_URL'),
        contract_address=os.environ.get('CONTRACT_ADDRESS'),
        poll_interval=os.environ.get('POLL_INTERVAL', 10))
    notifier.run()
