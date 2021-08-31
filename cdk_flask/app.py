#!/usr/bin/env python3

from aws_cdk import core

from cdk_stacks.webapp_stack import WebAppStack

app = core.App()
WebAppStack(app, "webapp1")
app.synth()
