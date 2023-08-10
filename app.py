#!/usr/bin/env python3
import aws_cdk as cdk
import yaml

from backend.component import Valohai

with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

    aws_account_id = str(config["aws_account_id"])
    aws_region = config["aws_region"]

env = cdk.Environment(account=aws_account_id, region=aws_region)

app = cdk.App()
Valohai(
    app,
    "ValohaiSandbox",
    env=env,
    aws_account_id=aws_account_id,
    vpc_id=config["vpc_id"],
    roi_subnet_id=config["roi_subnet_id"],
    db_subnet_ids=config["db_subnet_ids"],
    cache_subnet_ids=config["cache_subnet_ids"],
    domain=config["domain"],
    environment_name=config["environment_name"],
)

app.synth()
