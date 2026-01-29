# EKS cluster/control-plane SG (control-plane uses this)
resource "aws_security_group" "eks_cluster_sg" {
  name        = "eks-cluster-sg"
  description = "EKS cluster control plane SG"
  vpc_id      = aws_vpc.main.id

  # Allow EKS nodes to call cluster API (egress for nodes; here control plane ingress for 443 from nodes)
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_node_sg.id]
    description     = "Allow worker nodes to talk to control plane API"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "eks-cluster-sg" }
}

# EKS worker/node SG (for EC2 nodes that run pods)
resource "aws_security_group" "eks_node_sg" {
  name        = "eks-node-sg"
  description = "EKS worker nodes SG (for pods & node outbound)"
  vpc_id      = aws_vpc.main.id

  # allow node -> anywhere outbound (pull images, access MSK/RDS)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "eks-node-sg" }
}

# MSK security group
resource "aws_security_group" "msk_sg" {
  name        = "msk-sg"
  description = "Allow traffic to MSK brokers"
  vpc_id      = aws_vpc.main.id

  # Allow EKS worker nodes to connect to Kafka plaintext port 9092
  ingress {
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_node_sg.id]
    description     = "Kafka clients from EKS nodes"
  }

  # fallback: allow other VPC addresses (useful for bootstrap & troubleshooting)
  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "Allow VPC CIDR to Kafka (fallback)"
  }

  # Inter-broker communication
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
    description = "Broker-to-broker"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "msk-sg" }
}

# RDS security group
resource "aws_security_group" "rds_sg" {
  name        = "rds-sg"
  description = "Allow PostgreSQL traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_node_sg.id]
    description     = "Allow EKS worker nodes to access Postgres"
  }

  # fallback from VPC CIDR
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "Allow VPC CIDR to Postgres (fallback)"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "rds-sg" }
}
