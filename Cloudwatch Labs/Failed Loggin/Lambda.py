import boto3
import re

ec2 = boto3.client('ec2')

SECURITY_GROUP_ID = 'sg-xxxxxxxx'  # Replace with your EC2's Security Group ID

def lambda_handler(event, context):
    # Extract IP from log event message
    log_message = event['Records'][0]['Sns']['Message']
    ip_match = re.search(r'Failed password for .* from (\d+\.\d+\.\d+\.\d+)', log_message)
    
    if ip_match:
        attacker_ip = ip_match.group(1) + "/32"
        print(f"Blocking IP: {attacker_ip}")
        
        # Add rule to block IP
        ec2.revoke_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpProtocol='tcp',
            CidrIp=attacker_ip,
            FromPort=22,
            ToPort=22
        )
        
        ec2.authorize_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpProtocol='tcp',
            CidrIp=attacker_ip,
            FromPort=22,
            ToPort=22
        )
        
        print("IP blocked successfully.")
    else:
        print("No IP found in log message.")
