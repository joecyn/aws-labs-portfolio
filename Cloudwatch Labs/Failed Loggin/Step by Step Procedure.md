Step 1: Set up EC2 and Logging

Launch an EC2 instance (Amazon Linux/Ubuntu).

Install and configure CloudWatch Agent to send logs:
    sudo yum install amazon-cloudwatch-agent -y
Configure it to monitor /var/log/secure (Amazon Linux) or /var/log/auth.log (Ubuntu).


Step 2: Create a Log Group in CloudWatch

Go to CloudWatch → Logs → Create Log Group.

Name it: EC2FailedLoginLogs.

Configure the CloudWatch Agent to send logs there.



Step 3: Create a Metric Filter for Failed Logins

In CloudWatch → Logs → Log Groups → EC2FailedLoginLogs, click Create Metric Filter.

Filter pattern (for failed SSH login attempts):
    "Failed password for"


Create metric:

 .Namespace: EC2Security

 .Metric name: FailedLoginAttempts

 .Value: 1



 Step 4: Create a CloudWatch Alarm

   Go to CloudWatch → Alarms → Create Alarm.

       Select metric: EC2Security/FailedLoginAttempts.

   Set threshold:

       Static threshold = >=3 within 5 minutes.

  Actions:

       Trigger SNS topic (create one if needed).


Step 5: Create SNS Topic for Email Notifications

    Go to SNS → Create topic → Standard.

      Name: FailedLoginAlert.

    Create a subscription:

       Protocol: Email

       Endpoint: your-email@example.com

    Confirm subscription via email.


Step 6: Create Lambda Function to Block IP

    This Lambda will:

        Extract the attacker’s IP from the log event.

        Modify the Security Group to block the IP.

    IAM Role for Lambda: Needs ec2:ModifySecurityGroupRules, logs:DescribeLogStreams, logs:GetLogEvents.

Step 7: Connect Alarm → SNS → Lambda

    Set CloudWatch Alarm Action to publish to FailedLoginAlert SNS topic.

    Subscribe the Lambda function to the same SNS topic.