Project Overview

EC2 Instance (running a service, e.g., SSH or web server).

CloudWatch Logs to collect failed login attempts (from /var/log/secure or /var/log/auth.log).

CloudWatch Metric Filter to detect 3 failed logins within a time window.

CloudWatch Alarm to trigger when threshold is breached.

SNS Topic to send email notifications.

Lambda Function to automatically block the IP in the EC2 instance’s Security Group.