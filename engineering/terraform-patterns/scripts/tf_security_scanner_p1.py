# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_security_scanner_base import *  # noqa: F403,E402


DEMO_TF = """
provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

variable "db_password" {
  type    = string
  default = "supersecret123"
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_policy" "admin" {
  name = "admin-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

resource "aws_db_instance" "main" {
  engine               = "mysql"
  instance_class       = "db.t3.micro"
  password             = "hardcoded-password"
  publicly_accessible  = true
  skip_final_snapshot  = true
}
"""
SECRET_PATTERNS = [
    {
        "id": "SEC001",
        "name": "aws_access_key",
        "severity": "critical",
        "pattern": r'(?:access_key|aws_access_key_id)\s*=\s*"(AKIA[A-Z0-9]{16})"',
        "message": "AWS access key hardcoded in configuration",
        "fix": "Use environment variables, AWS profiles, or IAM roles instead",
    },
    {
        "id": "SEC002",
        "name": "aws_secret_key",
        "severity": "critical",
        "pattern": r'(?:secret_key|aws_secret_access_key)\s*=\s*"[A-Za-z0-9/+=]{40}"',
        "message": "AWS secret key hardcoded in configuration",
        "fix": "Use environment variables, AWS profiles, or IAM roles instead",
    },
    {
        "id": "SEC003",
        "name": "generic_password",
        "severity": "critical",
        "pattern": r'(?:password|passwd)\s*=\s*"[^"]{4,}"',
        "message": "Password hardcoded in resource or provider configuration",
        "fix": "Use a variable with sensitive = true, or fetch from Vault/SSM/Secrets Manager",
    },
    {
        "id": "SEC004",
        "name": "generic_secret",
        "severity": "critical",
        "pattern": r'(?:secret|token|api_key)\s*=\s*"[^"]{8,}"',
        "message": "Secret or token hardcoded in configuration",
        "fix": "Use a sensitive variable or secrets manager",
    },
    {
        "id": "SEC005",
        "name": "private_key",
        "severity": "critical",
        "pattern": r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
        "message": "Private key embedded in Terraform configuration",
        "fix": "Reference key file with file() function or use secrets manager",
    },
]
