#!/bin/bash

REGION="ap-south-1"
AMI_ID="ami-02b8269d5e85954ef"
INSTANCE_TYPE="t2.micro"
SUBNET_ID="subnet-0cc0bca8d7470dece"
VOLUME_SIZE=8
KEY_NAME="Jenkins"
SG_NAME="Jenkins-SG"

echo "✅ Creating Key Pair..."
aws ec2 create-key-pair \
  --region $REGION \
  --key-name $KEY_NAME \
  --query "KeyMaterial" \
  --output text > Jenkins.pem

chmod 400 Jenkins.pem
echo "✅ Key Pair saved as Jenkins.pem"

echo "✅ Creating Security Group..."
SG_ID=$(aws ec2 create-security-group \
  --group-name $SG_NAME \
  --description "Security Group for Jenkins" \
  --region $REGION \
  --query "GroupId" \
  --output text)

echo "✅ Security Group Created: $SG_ID"

echo "✅ Adding inbound rules..."
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0

echo "✅ Launching EC2 instance..."

INSTANCE_ID=$(aws ec2 run-instances \
  --region $REGION \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --subnet-id $SUBNET_ID \
  --associate-public-ip-address \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --block-device-mappings "DeviceName=/dev/xvda,Ebs={VolumeSize=$VOLUME_SIZE,VolumeType=gp3,DeleteOnTermination=true}" \
  --user-data "#!/bin/bash
yum update -y
amazon-linux-extras install java-openjdk11 -y
wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
yum install jenkins -y
systemctl enable jenkins
systemctl start jenkins
systemctl enable firewalld || true
systemctl stop firewalld || true
" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=Jenkins}]" \
  --query "Instances[0].InstanceId" \
  --output text)

echo "✅ EC2 Created: $INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances \
  --region $REGION \
  --instance-id $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text)

echo "✅ Public IP: $PUBLIC_IP"
echo "✅ Jenkins will be available in 2–3 minutes at:"
echo "👉 http://$PUBLIC_IP:8080"
echo "🔑 Key file: Jenkins.pem"
