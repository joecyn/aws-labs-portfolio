# Bastion host Terraform - simple setup (AWS)
# Usage: set variable "aws_region" and provide an existing EC2 key pair name in "key_name".

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "key_name" {
  type        = string
  description = "Existing EC2 Key Pair name to use for SSH access"
}

variable "allowed_ssh_cidr" {
  type    = string
  default = "0.0.0.0/0"
  description = "Source CIDR allowed to SSH to the bastion (change to your IP)"
}

# --- VPC ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "bastion-vpc"
  }
}

# Public subnet for bastion
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[0]
  tags = { Name = "public-subnet" }
}

# Private subnet for target EC2
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
  tags = { Name = "private-subnet" }
}

# Internet Gateway + route
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "bastion-igw" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "public-rt" }
}

resource "aws_route_table_association" "pub_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

# --- Security Groups ---
# Bastion SG: allow SSH from your IP only
resource "aws_security_group" "bastion_sg" {
  name        = "bastion-sg"
  description = "Allow SSH from admin IP"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from admin"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "bastion-sg" }
}

# Private EC2 SG: allow SSH only from bastion SG
resource "aws_security_group" "private_sg" {
  name        = "private-sg"
  description = "Allow SSH only from bastion"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "SSH from bastion"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    security_groups  = [aws_security_group.bastion_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "private-sg" }
}

# --- Data sources ---
data "aws_ami" "amazon_linux2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

data "aws_availability_zones" "available" {}

# --- Bastion EC2 ---
resource "aws_eip" "bastion_eip" {
  vpc = true
  depends_on = [aws_internet_gateway.igw]
}

resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.amazon_linux2.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  key_name               = var.key_name
  associate_public_ip_address = true
  vpc_security_group_ids = [aws_security_group.bastion_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y git
              # disable password auth
              sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config || true
              systemctl restart sshd || true
              EOF

  tags = { Name = "bastion-host" }
}

resource "aws_eip_association" "bastion_assoc" {
  allocation_id = aws_eip.bastion_eip.id
  instance_id   = aws_instance.bastion.id
}

# --- Private EC2 ---
resource "aws_instance" "private" {
  ami                    = data.aws_ami.amazon_linux2.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.private.id
  key_name               = var.key_name
  associate_public_ip_address = false
  vpc_security_group_ids = [aws_security_group.private_sg.id]

  tags = { Name = "private-ec2" }
}

# --- Outputs ---
output "bastion_public_ip" {
  value = aws_eip.bastion_eip.public_ip
}

output "private_instance_private_ip" {
  value = aws_instance.private.private_ip
}

output "bastion_ssh_command" {
  value = "ssh -i <path-to-key.pem> ec2-user@${aws_eip.bastion_eip.public_ip}"
}
