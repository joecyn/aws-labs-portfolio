Final Workflow

   Attacker fails SSH login 3 times →

   CloudWatch Agent sends log to CloudWatch Logs →

   Metric filter detects failure pattern →

   Alarm triggers SNS topic →

   SNS sends email + invokes Lambda →

   Lambda blocks IP in EC2 Security Group automatically.