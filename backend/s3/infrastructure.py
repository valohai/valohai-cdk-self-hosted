import aws_cdk.aws_s3 as s3
from aws_cdk import RemovalPolicy
from constructs import Construct


class Bucket(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        bucket_name: str,
    ):
        super().__init__(scope, id_)

        self.bucket = s3.Bucket(
            self,
            "valohai-bucket",
            bucket_name=bucket_name,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )
