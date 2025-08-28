# Lab 01: VPC with NAT Gateway

## 🎯 Objective
Create a VPC with public and private subnets, configure a NAT Gateway so instances in the private subnet can access the internet securely.

## 🏗️ Architecture
- VPC: 10.0.0.0/16
- Public Subnet: 10.0.1.0/24 → NAT Gateway
- Private Subnet: 10.0.2.0/24 → EC2 instance
- Internet Gateway attached

![Architecture Diagram](./diagrams/vpc-nat.png)

## 🔧 Steps
1. Created a VPC `10.0.0.0/16`.
2. Added public & private subnets.
3. Attached an Internet Gateway.
4. Created NAT Gateway in public subnet (with Elastic IP).
5. Updated private subnet route table → `0.0.0.0/0` to NAT Gateway.
6. Tested outbound connectivity from private EC2.

## ✅ Outcome
- Private EC2 can reach the internet (e.g., software updates).
- No inbound access from internet to private EC2.

## 📸 Screenshots
- [Route Table Config](./screenshots/route-table.png)
- [Private EC2 Internet Test](./screenshots/ping-test.png)

## 💡 Learnings
- NAT Gateway is AZ-specific; for high availability, deploy one per AZ.
- NAT Gateway is managed/scalable → better than NAT Instance.
