resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "RVM-VPC"
  }
}


resource "aws_efs_file_system" "my_efs" {
  creation_token = "my-efs"

  tags = {
    Name = "MyEFS"
  }
}