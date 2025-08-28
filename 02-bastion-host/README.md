# Lab 02: Bastion Host Setup

## 🎯 Objective
Deploy a bastion host in a public subnet to securely access private instances.

## 🏗️ Architecture
- Bastion Host in public subnet with Elastic IP
- Private instances accessible only via Bastion
- Security groups for restricted SSH

![Architecture Diagram](./diagrams/bastion-arch.png)



---

# 🛠 Steps to Set Up a Bastion Host in AWS

### 1. **Network Setup**

* Create (or use existing) **VPC** with both:

  * **Public subnet** (for the bastion host).
  * **Private subnet(s)** (for EC2 instances, databases, etc.).
* Attach an **Internet Gateway** to the VPC.
* Route public subnet traffic to the IGW, private subnet traffic to a NAT Gateway (if needed).

---

### 2. **Launch the Bastion Host**

* Launch an **EC2 instance** (Amazon Linux 2 or Ubuntu).
* Place it in the **public subnet**.
* Assign a **public IP or Elastic IP**.
* Attach a **security group**:

  * Inbound: allow **SSH (22)** (or RDP 3389 if Windows) only **from your IP**.
  * Outbound: allow to private subnet instances (usually unrestricted outbound).

---

### 3. **Configure Target Instances (Private Subnet)**

* Private EC2 instances should have **no public IPs**.
* Security group rules:

  * Allow **SSH (22)** or **RDP (3389)** inbound **only from the Bastion Host’s security group** (not from the internet).
* Outbound: allow internal VPC traffic.

---

### 4. **Connect via SSH Agent Forwarding**

On your local machine:

```bash
ssh -i my-key.pem ec2-user@<bastion-public-ip> -A
```

Then from the bastion host, connect to a private EC2:

```bash
ssh ec2-user@<private-ec2-ip>
```

---

### 5. **(Optional) Use AWS Systems Manager (SSM) Instead**

Instead of managing SSH keys:

* Attach **SSM Agent** role (AmazonSSMManagedInstanceCore) to instances.
* Use **Session Manager** in AWS console or CLI:

  ```bash
  aws ssm start-session --target <instance-id>
  ```
* This removes the need for a bastion host (preferred for production).

---

# ✅ Security Hardening Best Practices

* Restrict SSH access with **IAM + MFA + IP whitelisting**.
* Use **IAM roles**, not hardcoded keys.
* Patch & harden bastion host (fail2ban, disable root login, use audit logs).
* Enable **CloudTrail** and **VPC Flow Logs**.
* For high availability: deploy 2 bastion hosts across AZs with an **Auto Scaling group** behind a **Network Load Balancer**.

---

📌 **Quick Architecture Summary:**

* **Public Subnet** → Bastion Host (public IP, hardened).
* **Private Subnet** → Target EC2s (only accessible via Bastion).
* Security groups enforce:

  * Your IP → Bastion.
  * Bastion → Private EC2s.

---

