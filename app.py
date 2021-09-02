#!/usr/bin/env python3

from aws_cdk import core

from stacks.ethereum_contract_events_stack import EthereumContractEventsStack

app = core.App()
EthereumContractEventsStack(app, "app",
                            node_url='https://mainnet.infura.io/v3/33036dd577fa4493a03d2d3ab1098676',
                            contract_addresses={'CryptoPunks': '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'})
app.synth()
