resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids               = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    #cluster_security_group_id = aws_security_group.eks_cluster_sg.id
    # control_plane_endpoint_public_access = true (default)
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy_attachment,
  ]
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "main-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  instance_types  = ["t3.micro"]

  scaling_config {
    desired_size = 3
    max_size     = 3
    min_size     = 1
  }

  # Optional: use remote_access to attach your ssh key to instances (if you need SSH)
  dynamic "remote_access" {
    for_each = var.ssh_key_name != "" ? [1] : []
    content {
      ec2_ssh_key = var.ssh_key_name
      # security_groups = [aws_security_group.eks_node_sg.id] # remote ssh SG if desired
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_group_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_ec2_registry_read_only,
  ]
}
