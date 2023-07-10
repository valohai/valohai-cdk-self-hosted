import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from constructs import Construct


class LoadBalancer(Construct):
    def __init__(self, scope: Construct, id_: str, *, vpc: ec2.Vpc):
        super().__init__(scope, id_)

        self.sg_loadbalancer = ec2.SecurityGroup(
            self,
            "valohai-sg-loadbalancer",
            security_group_name="valohai-sg-loadbalancer",
            vpc=vpc,
            allow_all_outbound=True,
        )
        self.sg_loadbalancer.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            "valohai-roi-lb",
            load_balancer_name="valohai-roi-lb",
            vpc=vpc,
            internet_facing=True,
            security_group=self.sg_loadbalancer,
        )

        self.listener = load_balancer.add_listener("Listener", port=80)
        self.listener.connections.allow_default_port_from_any_ipv4("Open to the world")
