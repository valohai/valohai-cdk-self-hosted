# Valohai Self-Hosted CDK Template

This template allows you provision AWS resources for a self-hosted Valohai installation.

* Security Groups
* EC2 instance (valohai-master)
* RDS PostgreSQL database 
* ElastiCache Redis
* LoadBalancer
* IAM Roles
    * ValohaiMaster (attached to `valohai-master`)
    * ValohaiWorker (attached to all workers by default)
* S3 Bucket
* AWS Secrets Manager Secret to store RDS password
* AWS Systems Manager Parameter Store to store the SSH Key of `valohai-master`

To deploy:
1. Follow the steps below to activate the virtual environment and install requirements.
2. Review the `cdk.json` file for configuration options (VPC, subnet, tags, etc.)

## Options

Use the `config.yaml` to define AWS Account details:

* `aws_region` - Which AWS Region to deploy to
* `aws_account_id` - Which AWS Account to deploy to
* `lb_subnet_ids` - A list of subnets for the loadbalancer (public IPs)
* `roi_subnet_id` - A subnet for the main Valohai instance (private IP)
* `db_subnet_ids` - A list of subnets for the Postgres database (private IPs)
* `cache_subnet_ids` - A list of subnets for the Redis cache, which works as the job queue (private IPs)
* `worker_subnet_ids` - A list of subnets for the EC2 instacens that'll be used for Valohai workers (private IPs)
* `vpc_id`- The VPC ID to be used
* `environment_name` - Name of the environment (e.g. MyOrg-Valohai)
* `domain` - Domain to be used for the environment

## Run

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
