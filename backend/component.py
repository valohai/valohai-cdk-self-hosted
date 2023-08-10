from typing import Any

from aws_cdk import Stack
from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2_targets as targets
from constructs import Construct

from backend.compute.infrastructure import RoiInstance
from backend.iam.infrastructure import IAM
from backend.lb.infrastructure import LoadBalancer
from backend.postgres.infrastructure import Database
from backend.redis.infrastructure import Queue
from backend.s3.infrastructure import Bucket


class Valohai(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        aws_account_id: str,
        vpc_id: str,
        roi_subnet_id: str,
        db_subnet_ids: str,
        cache_subnet_ids: str,
        domain: str,
        environment_name: str,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        Tags.of(self).add("valohai", "1")

        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)
        roi_subnets = ec2.SubnetSelection(
            subnets=vpc.select_subnets(
                subnet_filters=[ec2.SubnetFilter.by_ids([roi_subnet_id])],
            ).subnets
        )

        db_subnets = ec2.SubnetSelection(
            subnets=vpc.select_subnets(
                subnet_filters=[ec2.SubnetFilter.by_ids(db_subnet_ids)]
            ).subnets
        )

        bucket_name = f"valohai-data-{aws_account_id}"

        self.bucket = Bucket(self, "valohai-data", bucket_name=bucket_name)

        iam = IAM(
            self,
            "valohai-iam",
            aws_account_id=aws_account_id,
            s3_bucket_name=bucket_name,
        )

        load_balancer = LoadBalancer(self, "valohai-loadbalancer", vpc=vpc)

        sg_workers = ec2.SecurityGroup(
            self,
            "valohai-sg-workers",
            security_group_name="valohai-sg-workers",
            description="Default security group for all Valohai managed EC2 workers",
            vpc=vpc,
            allow_all_outbound=True,
        )

        sg_master = ec2.SecurityGroup(
            self,
            "valohai-sg-master",
            security_group_name="valohai-sg-master",
            description="Security group for core Valohai Roi instance",
            vpc=vpc,
            allow_all_outbound=True,
        )

        sg_master.add_ingress_rule(
            peer=ec2.Peer.security_group_id(
                load_balancer.sg_loadbalancer.security_group_id
            ),
            connection=ec2.Port.tcp(8000),
            description="Allow access from LB",
        )

        sg_master.add_ingress_rule(
            ec2.Peer.ipv4("0.0.0.0/0"), ec2.Port.tcp(22), "Allow SSH access from user"
        )

        self.database = Database(
            self,
            "valohai-roi-database",
            vpc=vpc,
            subnets=db_subnets,
            sg_master=sg_master,
        )

        self.redis = Queue(
            self,
            "valohai-queue",
            vpc=vpc,
            subnet_ids=cache_subnet_ids,
            sg_master=sg_master,
            sg_workers=sg_workers,
        )

        compute = RoiInstance(
            self,
            "valohai-ec2",
            vpc=vpc,
            subnets=roi_subnets,
            security_group=sg_master,
            iam_role=iam.role_master,
            domain=domain,
            environment_name=environment_name,
        )
        load_balancer.listener.add_targets(
            "Target", port=8000, targets=[targets.InstanceTarget(compute.roi_instance)]
        )
