# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin5:
    def _terraform_gke_microservices(self) -> str:
        """Generate Terraform for GKE microservices pattern."""
        return f"""terraform {{
  required_version = ">= 1.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = var.project_id
  region  = var.region
}}

variable "project_id" {{
  description = "GCP project ID"
  type        = string
}}

variable "region" {{
  description = "GCP region"
  type        = string
  default     = "{self.region}"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "dev"
}}

variable "app_name" {{
  description = "Application name"
  type        = string
  default     = "{self.app_name}"
}}

# Enable required APIs
resource "google_project_service" "apis" {{
  for_each = toset([
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "servicenetworking.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  project = var.project_id
  service = each.value
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "${{var.app_name}}-vpc"
  auto_create_subnetworks = false
}}

resource "google_compute_subnetwork" "main" {{
  name          = "${{var.app_name}}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {{
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }}

  secondary_ip_range {{
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }}
}}

# GKE Autopilot Cluster
resource "google_container_cluster" "main" {{
  name     = "${{var.environment}}-${{var.app_name}}-cluster"
  location = var.region

  enable_autopilot = true

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  ip_allocation_policy {{
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }}

  release_channel {{
    channel = "REGULAR"
  }}

  depends_on = [google_project_service.apis["container.googleapis.com"]]
}}

# Private Services Access for Cloud SQL
resource "google_compute_global_address" "private_ip" {{
  name          = "private-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}}

resource "google_service_networking_connection" "private_vpc" {{
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip.name]
}}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {{
  name             = "${{var.environment}}-${{var.app_name}}-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {{
    tier              = "db-custom-2-8192"
    availability_type = "REGIONAL"

    backup_configuration {{
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
    }}

    ip_configuration {{
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }}

    disk_autoresize = true
  }}

  depends_on = [google_service_networking_connection.private_vpc]
}}

resource "google_sql_database" "app" {{
  name     = var.app_name
  instance = google_sql_database_instance.main.name
}}

# Memorystore Redis
resource "google_redis_instance" "cache" {{
  name           = "${{var.environment}}-${{var.app_name}}-cache"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  redis_version  = "REDIS_7_0"

  authorized_network = google_compute_network.main.id

  depends_on = [google_project_service.apis["redis.googleapis.com"]]

  labels = {{
    environment = var.environment
    app         = var.app_name
  }}
}}

# Outputs
output "cluster_name" {{
  description = "GKE cluster name"
  value       = google_container_cluster.main.name
}}

output "cloud_sql_connection" {{
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}}

output "redis_host" {{
  description = "Memorystore Redis host"
  value       = google_redis_instance.cache.host
}}
"""
