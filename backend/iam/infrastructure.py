import aws_cdk.aws_iam as iam
from constructs import Construct


class IAM(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        aws_account_id: str,
        s3_bucket_name: str,
    ):
        super().__init__(scope, id_)

        # ValohaiWorker
        worker_policy_document_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "autoscaling:SetInstanceProtection",
                    "Resource": "*",
                    "Effect": "Allow",
                    "Sid": "1",
                },
                {
                    "Action": "ec2:DescribeInstances",
                    "Resource": "*",
                    "Effect": "Allow",
                    "Sid": "2",
                },
            ],
        }

        worker_policy_document = iam.PolicyDocument.from_json(
            worker_policy_document_json
        )
        worker_policy = iam.ManagedPolicy(
            self,
            "valohai-policy-worker",
            managed_policy_name="valohai-policy-worker",
            document=worker_policy_document,
        )

        self.role_worker = iam.Role(
            self,
            "valohai-role-worker",
            role_name="valohai-role-worker",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        self.role_worker.add_managed_policy(worker_policy)

        # ValohaiMaster
        master_policy_document_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "2",
                    "Effect": "Allow",
                    "Action": [
                        "ec2:DescribeInstances",
                        "ec2:DescribeVpcs",
                        "ec2:DescribeKeyPairs",
                        "ec2:DescribeImages",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeInstanceTypes",
                        "ec2:DescribeLaunchTemplates",
                        "ec2:DescribeLaunchTemplateVersions",
                        "ec2:DescribeInstanceAttribute",
                        "ec2:DescribeRouteTables",
                        "ec2:DescribeInternetGateways",
                        "ec2:CreateTags",
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DescribeScalingActivities",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "AllowUpdatingSpotLaunchTemplates",
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateLaunchTemplate",
                        "ec2:CreateLaunchTemplateVersion",
                        "ec2:ModifyLaunchTemplate",
                        "ec2:RunInstances",
                        "ec2:RebootInstances",
                        "autoscaling:UpdateAutoScalingGroup",
                        "autoscaling:CreateOrUpdateTags",
                        "autoscaling:SetDesiredCapacity",
                        "autoscaling:CreateAutoScalingGroup",
                    ],
                    "Resource": "*",
                    "Condition": {
                        "ForAllValues:StringEquals": {"aws:ResourceTag/Valohai": "1"}
                    },
                },
                {
                    "Sid": "ServiceLinkedRole",
                    "Effect": "Allow",
                    "Action": "iam:CreateServiceLinkedRole",
                    "Resource": "arn:aws:iam::*:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling",
                },
                {
                    "Sid": "4",
                    "Effect": "Allow",
                    "Action": ["iam:PassRole", "iam:GetRole"],
                    "Resource": f"arn:aws:iam::{aws_account_id}:role/valohai-worker",
                },
                {
                    "Sid": "GetSSMParameters",
                    "Effect": "Allow",
                    "Action": [
                        "ssm:GetParameter",
                        "ssm:GetParameters",
                        "ssm:DescribeParameters",
                    ],
                    "Resource": "*",
                },
                {
                    "Action": "secretsmanager:GetRandomPassword",
                    "Resource": "*",
                    "Effect": "Allow",
                    "Sid": "1",
                },
                {
                    "Sid": "0",
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetResourcePolicy",
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                        "secretsmanager:ListSecretVersionIds",
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {"secretsmanager:ResourceTag/valohai": "1"}
                    },
                },
                {
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{s3_bucket_name}",
                        f"arn:aws:s3:::{s3_bucket_name}/*",
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ssm:GetServiceSetting",
                        "ssm:ResetServiceSetting",
                        "ssm:UpdateServiceSetting",
                    ],
                    "Resource": f"arn:aws:ssm:eu-west-2:{aws_account_id}:servicesetting/ssm/managed-instance/default-instance-management-role",
                },
                {
                    "Effect": "Allow",
                    "Action": ["iam:PassRole"],
                    "Resource": f"arn:aws:iam::{aws_account_id}:role/service-role/AWSSystemsManagerDefaultEC2InstanceManagementRole",
                    "Condition": {
                        "StringEquals": {"iam:PassedToService": ["ssm.amazonaws.com"]}
                    },
                },
                {
                    "Effect": "Allow",
                    "Action": ["ssm:StartSession"],
                    "Resource": [
                        f"arn:aws:ec2:eu-west-2:{aws_account_id}:instance/*",
                        f"arn:aws:ssm:eu-west-2:{aws_account_id}:document/SSM-SessionManagerRunShell",
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["ssm:TerminateSession", "ssm:ResumeSession"],
                    "Resource": ["arn:aws:ssm:*:*:session/*"],
                },
            ],
        }

        master_policy_document = iam.PolicyDocument.from_json(
            master_policy_document_json
        )

        master_policy = iam.ManagedPolicy(
            self,
            "valohai-policy-master",
            managed_policy_name="valohai-policy-master",
            document=master_policy_document,
        )

        self.role_master = iam.Role(
            self,
            "valohai-role-master",
            role_name="valohai-role-master",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        self.role_master.add_managed_policy(master_policy)

        # S3 Access
        multipart_policy_document_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "MultipartAccess",
                    "Effect": "Allow",
                    "Action": [
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucketVersions",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject",
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{s3_bucket_name}",
                        f"arn:aws:s3:::{s3_bucket_name}/*",
                    ],
                }
            ],
        }
        multipart_policy_document = iam.PolicyDocument.from_json(
            multipart_policy_document_json
        )
        multipart_policy = iam.ManagedPolicy(
            self,
            "valohai-policy-multipart",
            managed_policy_name="valohai-policy-multipart",
            document=multipart_policy_document,
        )

        role_multipart = iam.Role(
            self,
            "valohai-role-multipart",
            role_name="valohai-role-multipart",
            assumed_by=iam.ServicePrincipal("iam.amazonaws.com"),
        )
        role_multipart.add_managed_policy(multipart_policy)

        multipart_role_assume_policy_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{aws_account_id}:role/valohai-role-master"
                    },
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        role_multipart.assumeRolePolicy = iam.PolicyDocument.from_json(
            multipart_role_assume_policy_json
        )
