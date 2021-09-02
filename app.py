#!/usr/bin/env python3

from aws_cdk import core

from stacks.ethereum_contract_events_stack import EthereumContractEventsStack

app = core.App()

EthereumContractEventsStack(app,
                            'EthereumContractEventsStack',
                            node_url='https://mainnet.infura.io/v3/33036dd577fa4493a03d2d3ab1098676',
                            contract_addresses={
                                'CryptoPunks': '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB',
                                'MeeBits': '0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7',
                                'MutantApeYachtClub': '0x60E4d786628Fea6478F785A6d7e704777c86a7c6'
                            })
app.synth()
