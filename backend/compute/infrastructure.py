import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_ssm as ssm
from constructs import Construct


class RoiInstance(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        vpc: ec2.Vpc,
        subnets: ec2.SubnetSelection,
        security_group: ec2.SecurityGroup,
        iam_role: iam.Role,
        domain: str,
        environment_name: str,
    ):
        super().__init__(scope, id_)

        # Generate a Key Pair and save the Private Key to AWS Systems Manager Parameter Store
        master_key_pair = ec2.CfnKeyPair(
            self, "valohai-master-key-pair", key_name="valohai-master-key-pair"
        )

        # Generate secrets
        secretsmanager.Secret(
            self,
            "valohai-secret-repo",
            secret_name="valohai-secret-repo",
            description="Secure repository key for Valohai",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_characters="\"@/\\ '",
                exclude_punctuation=True,
                password_length=30,
            ),
        )

        secretsmanager.Secret(
            self,
            "valohai-secret-secret",
            secret_name="valohai-secret-secret",
            description="Secure secret key for Valohai",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_characters="\"@/\\ '",
                exclude_punctuation=True,
                password_length=30,
            ),
        )

        secretsmanager.Secret(
            self,
            "valohai-secret-jwt",
            secret_name="valohai-secret-jwt",
            description="Secure repository key for Valohai",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_characters="\"@/\\ '",
                exclude_punctuation=True,
                password_length=30,
            ),
        )

        ssm.StringParameter(
            self,
            "valohai-domain",
            allowed_pattern=".*",
            description="The Domain for the Valohai installation",
            parameter_name="valohai-domain",
            string_value=domain,
        )

        ssm.StringParameter(
            self,
            "valohai-env-name",
            allowed_pattern=".*",
            description="The Environemnt name for the Valohai installation",
            parameter_name="valohai-env-name",
            string_value=environment_name,
        )

        # Find the latest Valohai Roi image
        valohai_roi_image = ec2.LookupMachineImage(
            name="valohai-roi-*", owners=["635691382966"], windows=False
        )

        with open(
            "backend/compute/roi_user_data.sh", encoding="UTF-8"
        ) as user_data_file:
            user_data = user_data_file.read()

        self.roi_instance = ec2.Instance(
            self,
            "valohai_roi",
            instance_name="valohai-roi",
            machine_image=valohai_roi_image,
            instance_type=ec2.InstanceType("m5a.xlarge"),
            key_name=master_key_pair.key_name,
            vpc=vpc,
            vpc_subnets=subnets,
            security_group=security_group,
            role=iam_role,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1", volume=ec2.BlockDeviceVolume.ebs(32)
                )
            ],
            require_imdsv2=True,
            user_data=ec2.UserData.custom(user_data),
        )
