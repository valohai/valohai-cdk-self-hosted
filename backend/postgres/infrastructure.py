import aws_cdk as cdk
import aws_cdk.aws_rds as rds
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_secretsmanager as secretsmanager
from constructs import Construct


class Database(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        vpc: ec2.Vpc,
        subnets: ec2.SubnetSelection,
        sg_master: ec2.SecurityGroup
    ):
        super().__init__(scope, id_)

        engine = rds.DatabaseInstanceEngine.postgres(
            version=rds.PostgresEngineVersion.VER_14_3
        )

        sg_database = ec2.SecurityGroup(
            self,
            "valohai-sg-database",
            security_group_name="valohai-sg-database",
            vpc=vpc,
            allow_all_outbound=True,
        )
        sg_database.add_ingress_rule(
            ec2.Peer.security_group_id(sg_master.security_group_id),
            ec2.Port.tcp(5432),
            "Allow access from Valohai App (Roi)",
        )

        db_subnet_group = rds.SubnetGroup(
            self,
            id="valohai_postgres_subnet_group",
            subnet_group_name="valohai_postgres_subnet_group",
            vpc=vpc,
            description="Subnet group for Valohai Roi Database (PostgreSQL)",
            vpc_subnets=subnets,
        )

        db_password = secretsmanager.Secret(
            self,
            "valohai-secret-dbpassword",
            secret_name="valohai-secret-dbpassword",
            description="Valohai Roi DB Credentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_characters="\"@/\\ '",
                exclude_punctuation=True,
                generate_string_key="password",
                password_length=30,
                secret_string_template='{"username":"roi"}',
            ),
        )

        cluster_credentials = rds.Credentials.from_secret(db_password, "roi")

        self.rds_instance = rds.DatabaseInstance(
            self,
            "roidb",
            engine=engine,
            instance_type=ec2.InstanceType("m5.xlarge"),
            allocated_storage=20,
            storage_encrypted=True,
            multi_az=True,
            publicly_accessible=False,
            port=5432,
            auto_minor_version_upgrade=True,
            iam_authentication=True,
            cloudwatch_logs_exports=["postgresql", "upgrade"],
            copy_tags_to_snapshot=True,
            parameter_group=None,
            database_name="roidb",
            credentials=cluster_credentials,
            vpc=vpc,
            security_groups=[sg_database],
            subnet_group=db_subnet_group,
            preferred_maintenance_window="Mon:00:00-Mon:03:00",
            preferred_backup_window="03:00-06:00",
            backup_retention=cdk.Duration.days(5),
            deletion_protection=True,
        )

        ssm.StringParameter(
            self,
            "valohai-db-url",
            allowed_pattern=".*",
            description="The URL for the Valohai Database",
            parameter_name="valohai-db-url",
            string_value=self.rds_instance.db_instance_endpoint_address,
        )
