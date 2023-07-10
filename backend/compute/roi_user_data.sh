#!/bin/bash

sudo apt-get update
sudo apt-get install jq -y

sudo systemctl stop roi
export AWS_PROFILE=default
export ROI_AUTO_MIGRATE=true

sed -i '/^ExecStart=/usr/bin/docker run \/a --net=host \' /etc/systemd/system/roi.service
sudo systemctl daemon-reload

export REPO_PRIVATE_KEY=`aws secretsmanager get-secret-value --secret-id valohai-secret-repo | sed -n 's|.*"SecretString": *"\([^"]*\)".*|\1|p'`
export SECRET_KEY=`aws secretsmanager get-secret-value --secret-id valohai-secret-secret | sed -n 's|.*"SecretString": *"\([^"]*\)".*|\1|p'`
export JWT_KEY=`aws secretsmanager get-secret-value --secret-id valohai-secret-repo | sed -n 's|.*"SecretString": *"\([^"]*\)".*|\1|p'`
export REDIS_URL=`aws ssm get-parameter --name valohai-redis-url --with-decryption | sed -n 's|.*"Value": *"\([^"]*\)".*|\1|p'`
export DB_URL=`aws ssm get-parameter --name valohai-db-url --with-decryption | sed -n 's|.*"Value": *"\([^"]*\)".*|\1|p'`
export DB_PASSWORD=`aws secretsmanager get-secret-value --secret-id valohai-secret-dbpassword --query SecretString --output text | jq -r .password`

export DOMAIN=`aws ssm get-parameter --name valohai-domain --with-decryption | sed -n 's|.*"Value": *"\([^"]*\)".*|\1|p'`
export ENV_NAME=`aws ssm get-parameter --name valohai-env-name --with-decryption | sed -n 's|.*"Value": *"\([^"]*\)".*|\1|p'`
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` && export AWS_REGION=`curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//'`
export AWS_ACCOUNT=`aws sts get-caller-identity | jq -r .Account`

sed -i "s|URL_BASE=|URL_BASE=$DOMAIN|" /etc/roi.config
sed -i "s|AWS_REGION=|AWS_REGION=$AWS_REGION|" /etc/roi.config
sed -i "s|AWS_S3_BUCKET_NAME=|AWS_S3_BUCKET_NAME=$BUCKET_NAME|" /etc/roi.config
sed -i "s|AWS_S3_MULTIPART_UPLOAD_IAM_ROLE=|AWS_S3_MULTIPART_UPLOAD_IAM_ROLE=arn:aws:iam::$AWS_ACCOUNT:role/valohai-role-multipart|" /etc/roi.config
sed -i "s|CELERY_BROKER=|CELERY_BROKER=redis://$REDIS_URL:6379|" /etc/roi.config
sed -i "s|DATABASE_URL=|DATABASE_URL=psql://roi:$DB_PASSWORD@$DB_URL:5432/roidb|" /etc/roi.config
sed -i "s|PLATFORM_LONG_NAME=|PLATFORM_LONG_NAME=$ENV_NAME|" /etc/roi.config
sed -i "s|REPO_PRIVATE_KEY_SECRET=|REPO_PRIVATE_KEY_SECRET=$REPO_PRIVATE_KEY|" /etc/roi.config
sed -i "s|SECRET_KEY=|SECRET_KEY=$SECRET_KEY|" /etc/roi.config
sed -i "s|STATS_JWT_KEY=|STATS_JWT_KEY=$JWT_KEY|" /etc/roi.config

sudo systemctl start roi

sudo docker run -it --env-file=/etc/roi.config valohai/roi:latest python manage.py migrate
sudo docker run -it --env-file=/etc/roi.config valohai/roi:latest python manage.py roi_init --mode dev

sudo snap start amazon-ssm-agent