from aws_cdk import (
        core,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_sns as sns,
        aws_logs as logs,
        aws_events as events,
        aws_events_targets as events_targets,
        aws_iam as iam,
)

class EthereumContractEventsStack(core.Stack):
    """
    A class used to represent and initialise the AWS Cloudformation stack using CDK
    """
    
    def __init__(self, scope: core.Construct, id: str, node_url: str, contract_addresses: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        vpc = self._create_vpc()
        ecs_cluster = self._create_ecs_cluster(vpc)
        event_bus = self._create_event_bus(name='ethereum_contract_events')
        ecs_services = self._create_services(ecs_cluster, node_url, contract_addresses)
        self._create_permissions(ecs_services, event_bus)


    def _create_vpc(self):
        """Creates a VPC with an internet gateway and public/private

        Parameters
        ----------
        file_loc : str
            The file location of the spreadsheet
        print_cols : bool, optional
            A flag used to print the columns to the console (default is
            False)
    
        Returns
        -------
        list
            a list of strings used that are the header columns
        """
        vpc = ec2.Vpc(self, 'FargateFlaskVPC', cidr='10.0.0.0/16')
        return vpc

    def _create_services(self, cluster, node_url, contract_addresses):
        """Creates a serverless Fargate service for ECS from a local dockerfile
        for each ethereum contract address

        Parameters
        ----------
        ecs_cluster : aws-cdk.aws_ecs.Cluster
            The ECS cluster to run the service
        node_url : string
            The URL of an ethereum node
        contract_addresses : dict
            A dictionary of contract names to contract addresses
    
        Returns
        -------
        list<aws-cdk.ecs.FargateService>
            A list of serverless fargate services
        """
        services = []
        for contract_name, contract_address in contract_addresses.items():
            fargate_task_definition = ecs.FargateTaskDefinition(
                self,
                "{}TaskDefinition".format(contract_name),
                memory_limit_mib=512,
                cpu=256
            )
            container = fargate_task_definition.add_container("{}Container".format(contract_name),
            image=ecs.ContainerImage.from_asset('containers/ethereum-contract-events-relay'),
            environment={# clear text, not for sensitive data
                "NODE_URL": node_url,
                "CONTRACT_ADDRESS": contract_address
                },
            logging=ecs.AwsLogDriver(stream_prefix="{}EthereumContractEvents".format(contract_name), mode=ecs.AwsLogDriverMode.NON_BLOCKING)
            )
            service = ecs.FargateService(self, "{}Service".format(contract_name),
                cluster=cluster,
                task_definition=fargate_task_definition,
                desired_count=1
            )
            services.append(service)
        return services

    def _create_ecs_cluster(self, vpc):
        """Creates an ECS cluster inside  a Vpc

        Parameters
        ----------
        vpc : aws-cdk.aws_ec2.Vpc
            The Vpc to deploy the cluster into
    
        Returns
        -------
        aws-cdk.aws_ecs.Cluster
            An ECS cluster
        """
        ecs_cluster = ecs.Cluster(self, 'Cluster', vpc=vpc)
        return ecs_cluster

    def _create_event_bus(self, name):
        """Creates an event bus for ethereum contract events,
        the corresponding rule, and example SNS topic and cloudwatch 
        targets

        Parameters
        ----------
        name: string
            The name of the event bus
        
        Returns
        -------
        aws-cdk.aws_events.EventBus
            An AWS EventBriddge event bus
        """
        event_bus = events.EventBus(self, "EventBus", event_bus_name=name)
        rule = events.Rule(self, "rule", event_bus=event_bus,
                           event_pattern={
                               "account": [self.account]}
        )
        topic = sns.Topic(self, "Topic", display_name="Ethereum contract events topic",
                              topic_name="EthereumContractEventsTopic")
        log_group = logs.LogGroup(self, "EthereumContractEventsLogGroup",
                              log_group_name="EthereumContractEventsLogGroup"
        )
        rule.add_target(events_targets.SnsTopic(topic))
        rule.add_target(events_targets.CloudWatchLogGroup(log_group))
        return event_bus


    def _create_permissions(self, ecs_services, event_bus):
        """Enables the fargate service to carry out all actions on 
        the dedicated eventbridge event bus

        Parameters
        ----------
        ecs_services: list<aws-cdk.ecs.FargateService>
            A list of serverless fargate services
        event_bus: aws-cdk.aws_events.EventBus
            An AWS EventBriddge event bus
    
        Returns
        -------
        """
        for ecs_service in ecs_services:
            ecs_service.task_definition.add_to_task_role_policy(
                iam.PolicyStatement(actions=["events:*"],
                resources=[event_bus.event_bus_arn]))
    
