import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_elasticache as elasticache
from constructs import Construct


class Queue(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        vpc: ec2.Vpc,
        subnet_ids: str,
        sg_master: ec2.SecurityGroup,
        sg_workers: ec2.SecurityGroup
    ):
        super().__init__(scope, id_)

        # Valohai SG Queue
        sg_redis_queue = ec2.SecurityGroup(
            self,
            "valohai-sg-queue",
            security_group_name="valohai-sg-queue",
            description="for Valohai Queue",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # Allow connections from Roi
        sg_redis_queue.add_ingress_rule(
            ec2.Peer.security_group_id(sg_master.security_group_id),
            ec2.Port.tcp(6379),
            description="Allow access from roi",
        )
        # Allow connections from workers
        sg_redis_queue.add_ingress_rule(
            ec2.Peer.security_group_id(sg_workers.security_group_id),
            ec2.Port.tcp(6379),
            description="Allow access from workers",
        )

        cache_subnet_group = elasticache.CfnSubnetGroup(
            scope=self,
            cache_subnet_group_name="valohai-redis-cache-subnet-group",
            id="valohai_redis_cache_subnet_group",
            subnet_ids=subnet_ids,
            description="Subnet Group for Redis job queue in Valohai",
        )

        self.redis_cluster = elasticache.CfnCacheCluster(
            scope=self,
            id="valohai-queue-redis",
            cluster_name="valohai-queue-redis",
            engine="redis",
            cache_node_type="cache.m5.xlarge",
            num_cache_nodes=1,
            engine_version="6.2",
            snapshot_retention_limit=5,
            cache_subnet_group_name=cache_subnet_group.cache_subnet_group_name,
            vpc_security_group_ids=[sg_redis_queue.security_group_id],
        )

        # https://github.com/aws/aws-cdk/issues/6935#issuecomment-612637197
        self.redis_cluster.add_dependency(cache_subnet_group)

        ssm.StringParameter(
            self,
            "valohai-redis-url",
            allowed_pattern=".*",
            description="The URL for the Valohai Redis Queue",
            parameter_name="valohai-redis-url",
            string_value=self.redis_cluster.attr_redis_endpoint_address,
        )
