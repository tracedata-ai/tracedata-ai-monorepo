# ---------------------------------------------------------------------------
# locals — shared tags applied to every resource to avoid repetition
# ---------------------------------------------------------------------------
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# VPC — core network boundary with DNS support enabled
# ---------------------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

# ---------------------------------------------------------------------------
# Public Subnet 1 — in availability_zone_1, auto-assigns public IPs
# ---------------------------------------------------------------------------
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_1_cidr
  availability_zone       = var.availability_zone_1
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-subnet-1"
    Tier = "Public"
  })
}

# ---------------------------------------------------------------------------
# Public Subnet 2 — in availability_zone_2, auto-assigns public IPs
# ---------------------------------------------------------------------------
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_2_cidr
  availability_zone       = var.availability_zone_2
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-subnet-2"
    Tier = "Public"
  })
}

# ---------------------------------------------------------------------------
# Private Subnet 1 — in availability_zone_1, no public IPs
# ---------------------------------------------------------------------------
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_1_cidr
  availability_zone = var.availability_zone_1

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-subnet-1"
    Tier = "Private"
  })
}

# ---------------------------------------------------------------------------
# Private Subnet 2 — in availability_zone_2, no public IPs
# ---------------------------------------------------------------------------
resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_2_cidr
  availability_zone = var.availability_zone_2

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-subnet-2"
    Tier = "Private"
  })
}

# ---------------------------------------------------------------------------
# Internet Gateway — allows the VPC to communicate with the public internet
# ---------------------------------------------------------------------------
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-igw"
  })
}

# ---------------------------------------------------------------------------
# Elastic IP — static public IP address allocated for the NAT Gateway
# ---------------------------------------------------------------------------
resource "aws_eip" "nat" {
  domain = "vpc"

  # Ensure the IGW exists before allocating the EIP so the EIP can be
  # released cleanly on destroy without a dependency conflict.
  depends_on = [aws_internet_gateway.igw]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  })
}

# ---------------------------------------------------------------------------
# NAT Gateway — placed in public_1 so private subnets can reach the internet
# ---------------------------------------------------------------------------
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id

  # NAT Gateway needs the IGW to be available before it can route traffic
  depends_on = [aws_internet_gateway.igw]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat-gw"
  })
}

# ---------------------------------------------------------------------------
# Public Route Table — routes all egress traffic (0.0.0.0/0) via the IGW
# ---------------------------------------------------------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-rt"
  })
}

# ---------------------------------------------------------------------------
# Public Route Table Associations — attach both public subnets to the table
# ---------------------------------------------------------------------------
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# ---------------------------------------------------------------------------
# Private Route Table — routes all egress traffic (0.0.0.0/0) via the NAT GW
# ---------------------------------------------------------------------------
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-rt"
  })
}

# ---------------------------------------------------------------------------
# Private Route Table Associations — attach both private subnets to the table
# ---------------------------------------------------------------------------
resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}