resource "aws_db_subnet_group" "default" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  tags = { Name = "Main DB subnet group" }
}

resource "aws_db_instance" "default" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "13"
  instance_class       = "db.t3.micro"
  db_name              = "sensor_db"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres13"
  db_subnet_group_name = aws_db_subnet_group.default.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot  = true
  publicly_accessible  = false
  multi_az             = false
  tags = { Name = "main-postgres" }
}
