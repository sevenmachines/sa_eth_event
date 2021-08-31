from aws_cdk import (
        core,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_ecs_patterns as ecs_patterns,
        aws_iam as iam,
        aws_lambda as _lambda,
        aws_s3 as s3,
        aws_dynamodb as ddb,
        aws_rds as rds,
        aws_s3_notifications as s3_notifications
)

class WebAppStack(core.Stack):
    """
    A class used to represent an initialise an AWS Cloudformation stack

    """
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        vpc = self._create_vpc()
        ecs_cluster = self._create_ecs_cluster(vpc)
        db_cluster = self._create_database(vpc)
        s3_bucket = self._create_s3()
        ecs_service = self._create_service(ecs_cluster, s3_bucket, db_cluster)
        self._create_permissions(ecs_service, s3_bucket, db_cluster)

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

    def _create_service(self, ecs_cluster, s3_bucket, db_cluster):
        """Creates a serverless Fargate service for ECS from a local dockerfile.
        The service is fronted by an application load balancer.

        Parameters
        ----------
        ecs_cluster : aws-cdk.aws_ecs.Cluster
            The ECS cluster to run the service
        s3_bucket : aws-cdk.aws_s3.Bucket
            An S3 bucket for container use
        db_cluster : aws-cdk.aws_rds.DatabaseCluster
            An Aurora database for container use
    
        Returns
        -------
        aws-cdk.ecs_patterns.ApplicationLoadBalancedFargateService
            A serverless fargate fronted by an application load balancer
        """
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, 'FargateService',
            cluster=ecs_cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset('docker-flask'),
                container_port=5000,
                environment={
                    'S3_BUCKET': s3_bucket.bucket_name,
                    'DB_SECRETS': db_cluster.secret.secret_name,
                    'DB_SECRETS_ARN': db_cluster.secret.secret_arn
                    
                })
        )
        service.target_group.configure_health_check(path='/health')
        return service

    def _create_s3(self):
        """Creates an S3 bucket

        Parameters
        ----------
    
        Returns
        -------
        aws-cdk.aws_s3.Bucket
            A private S3 bucket
        """
        bucket = s3.Bucket(self, 'VideoBucket')
        return bucket

    def _create_database(self, vpc):
        """Creates a serverless Aurora Posgres database inside a vpc's private 
        subnets.

        Parameters
        ----------
        vpc : aws-cdk.aws_ec2.Vpc
            The Vpc to deploy the database instances into
    
        Returns
        -------
        aws-cdk.aws_rds.DatabaseCluster
            A cluster of aurora postgres instances
        """
        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        db_cluster = rds.DatabaseCluster(self, "Database",
            engine=rds.DatabaseClusterEngine.aurora_postgres(version=rds.AuroraPostgresEngineVersion.VER_10_16),
            instance_props={
                "vpc_subnets": {
                    "subnet_type": ec2.SubnetType.PRIVATE
                },
                "vpc": vpc
            }
        )
        return db_cluster

    def _create_permissions(self, ecs_service, s3_bucket, db_cluster):
        """Enables the fargate service in the ECS cluster the permissions
        to store data in an s3 bucket, and access the database cluster

        Parameters
        ----------
        aws-cdk.ecs_patterns.ApplicationLoadBalancedFargateService
            A serverless fargate fronted by an application load balancer
        s3_bucket : aws-cdk.aws_s3.Bucket
            An S3 bucket for container use
        db_cluster : aws-cdk.aws_rds.DatabaseCluster
            An Aurora database for container use
    
        Returns
        -------
        """
        ecs_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["s3:*"], resources=[s3_bucket.bucket_arn+"/*"]))
        ecs_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["secretsmanager:GetSecretValue"], resources=[db_cluster.secret.secret_arn]))
        

    