resource "aws_msk_cluster" "main" {
  cluster_name           = "main-msk-cluster"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type  = "kafka.t3.small"
    client_subnets = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    storage_info {
      ebs_storage_info { volume_size = 10 }
    }
    security_groups = [aws_security_group.msk_sg.id]
  }
    encryption_info {
    encryption_in_transit {
      client_broker = "PLAINTEXT"
      in_cluster    = true
    }
  }
  tags = { Name = "main-msk-cluster" }
}
