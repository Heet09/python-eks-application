# resource "aws_security_group" "kafka_sg" {
#   name        = "kafka-sg"
#   description = "Allow traffic to Kafka instance"
#   vpc_id      = aws_vpc.main.id
# 
# 
#   # Allow all outbound traffic
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }
# 
# resource "aws_instance" "kafka_ec2" {
#   ami           = "ami-00ca32bbc84273381" # Amazon Linux 2 AMI (HVM), SSD Volume Type
#   instance_type = "t3.micro"
#   subnet_id     = aws_subnet.private.id
#   vpc_security_group_ids = [aws_security_group.kafka_sg.id]
# 
#   user_data = <<-EOF
#               #!/bin/bash
#               yum update -y
#               yum install -y docker
#               service docker start
#               usermod -a -G docker ec2-user
#               curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
#               chmod +x /usr/local/bin/docker-compose
#               ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
#               
#               cat <<EOT > /home/ec2-user/docker-compose.yml
# version: '3.8'
# services:
#   zookeeper:
#     image: confluentinc/cp-zookeeper:7.4.0
#     hostname: zookeeper
#     container_name: zookeeper
#     ports:
#       - "2181:2181"
#     environment:
#       ZOOKEEPER_CLIENT_PORT: 2181
#       ZOOKEEPER_TICK_TIME: 2000
# 
#   kafka:
#     image: confluentinc/cp-kafka:7.4.0
#     hostname: kafka
#     container_name: kafka
#     depends_on:
#       - zookeeper
#     ports:
#       - "9092:9092"
#     environment:
#       KAFKA_BROKER_ID: 1
#       KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
#       KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
#       KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://:9092
#       KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
#       KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
#       KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
#       KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
# EOT
# 
#               docker-compose -f /home/ec2-user/docker-compose.yml up -d
#               EOF
# 
#   tags = {
#     Name = "kafka-instance"
#   }
# }