# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_module_analyzer_base import *  # noqa: F403,E402


DEMO_FILES = {
    "main.tf": """
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name = "web-server"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket-12345"
}

resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
}

module "vpc" {
  source = "./modules/vpc"
  cidr   = var.vpc_cidr
}
""",
    "variables.tf": """
variable "ami_id" {
  type = string
}

variable "instance_type" {
  default = "t3.micro"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
""",
    "outputs.tf": """
output "instance_id" {
  value = aws_instance.web_server.id
}

output "bucket_arn" {
  value       = aws_s3_bucket.data.arn
  description = "ARN of the data S3 bucket"
}
""",
}
VALID_RESOURCE_NAME = re.compile(r'^[a-z][a-z0-9_]*$')
EXPECTED_FILES = {
    "main.tf": "Primary resources",
    "variables.tf": "Input variables",
    "outputs.tf": "Output values",
    "versions.tf": "Provider and Terraform version requirements",
}
OPTIONAL_FILES = {
    "locals.tf": "Computed local values",
    "data.tf": "Data sources",
    "backend.tf": "Remote state backend configuration",
    "providers.tf": "Provider configuration",
    "README.md": "Module documentation",
}
def find_tf_files(directory):
    """Find all .tf files in a directory (non-recursive)."""
    tf_files = {}
    for entry in sorted(os.listdir(directory)):
        if entry.endswith(".tf"):
            filepath = os.path.join(directory, entry)
            with open(filepath, encoding="utf-8") as f:
                tf_files[entry] = f.read()
    return tf_files
def parse_resources(content):
    """Extract resource declarations from HCL content."""
    resources = []
    for match in re.finditer(
        r'^resource\s+"([^"]+)"\s+"([^"]+)"', content, re.MULTILINE
    ):
        resources.append({
            "type": match.group(1),
            "name": match.group(2),
            "provider": match.group(1).split("_")[0],
        })
    return resources
def parse_data_sources(content):
    """Extract data source declarations."""
    sources = []
    for match in re.finditer(
        r'^data\s+"([^"]+)"\s+"([^"]+)"', content, re.MULTILINE
    ):
        sources.append({"type": match.group(1), "name": match.group(2)})
    return sources
