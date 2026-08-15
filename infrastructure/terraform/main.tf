terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  backend "s3" {
    bucket         = "miracle-birds-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "miracle-birds-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "MiracleBirds"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ==================== VPC ====================
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "miracle-birds-${var.environment}"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# ==================== EKS CLUSTER ====================
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "miracle-birds-${var.environment}"
  cluster_version = "1.29"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    # General purpose nodes
    general = {
      instance_types = ["t3.xlarge"]
      min_size       = 3
      max_size       = 10
      desired_size   = 3
      disk_size      = 50

      labels = {
        role = "general"
      }
    }

    # AI/ML workload nodes (GPU-enabled for ML inference)
    ai_ml = {
      instance_types = ["g4dn.xlarge"]
      min_size       = 1
      max_size       = 5
      desired_size   = 2
      disk_size      = 100

      labels = {
        role = "ai-ml"
      }

      taints = {
        gpu = {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
}

# ==================== RDS POSTGRESQL ====================
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "miracle-birds-${var.environment}"

  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.r6g.xlarge"
  allocated_storage    = 100
  max_allocated_storage = 1000

  db_name  = "miracle_birds"
  username = "miracle_birds_admin"
  port     = "5432"

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.rds_security_group.security_group_id]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  backup_retention_period         = 30
  skip_final_snapshot             = false
  deletion_protection             = true

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60
  monitoring_role_arn                   = aws_iam_role.rds_enhanced_monitoring.arn

  parameters = [
    {
      name  = "log_connections"
      value = "1"
    },
    {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements,vector"
    }
  ]
}

# ==================== ELASTICACHE REDIS ====================
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "miracle-birds-${var.environment}"
  description          = "Miracle Birds Redis cluster"

  node_type            = "cache.r6g.large"
  port                 = 6379
  num_cache_clusters   = 2

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [module.redis_security_group.security_group_id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  maintenance_window       = "tue:02:00-tue:03:00"
  snapshot_retention_limit = 7
  snapshot_window          = "00:00-01:00"

  automatic_failover_enabled = true
  multi_az_enabled           = true

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_logs.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }
}

# ==================== S3 BUCKETS ====================
resource "aws_s3_bucket" "assets" {
  bucket = "miracle-birds-assets-${var.environment}"
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ==================== SECRETS MANAGER ====================
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "miracle-birds/${var.environment}/app"
  description             = "Application secrets for Miracle Birds"
  recovery_window_in_days = 7
}

# ==================== CLOUDWATCH LOG GROUPS ====================
resource "aws_cloudwatch_log_group" "application" {
  name              = "/miracle-birds/${var.environment}/application"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "redis_slow_logs" {
  name              = "/miracle-birds/${var.environment}/redis-slow-logs"
  retention_in_days = 30
}
