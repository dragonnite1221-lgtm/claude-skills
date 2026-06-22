# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin4:
    def _terraform_serverless_web(self) -> str:
        """Generate Terraform for serverless web pattern."""
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
    "run.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "monitoring.googleapis.com",
  ])
  project = var.project_id
  service = each.value
}}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run" {{
  account_id   = "${{var.app_name}}-run-sa"
  display_name = "${{var.app_name}} Cloud Run Service Account"
}}

resource "google_project_iam_member" "firestore_user" {{
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${{google_service_account.cloud_run.email}}"
}}

resource "google_project_iam_member" "secret_accessor" {{
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${{google_service_account.cloud_run.email}}"
}}

# Firestore Database
resource "google_firestore_database" "default" {{
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.apis["firestore.googleapis.com"]]
}}

# Cloud Run Service
resource "google_cloud_run_v2_service" "api" {{
  name     = "${{var.environment}}-${{var.app_name}}-api"
  location = var.region

  template {{
    service_account = google_service_account.cloud_run.email

    containers {{
      image = "${{var.region}}-docker.pkg.dev/${{var.project_id}}/${{var.app_name}}/${{var.app_name}}:latest"

      resources {{
        limits = {{
          cpu    = "1000m"
          memory = "512Mi"
        }}
      }}

      env {{
        name  = "PROJECT_ID"
        value = var.project_id
      }}

      env {{
        name  = "ENVIRONMENT"
        value = var.environment
      }}
    }}

    scaling {{
      min_instance_count = 0
      max_instance_count = 10
    }}
  }}

  depends_on = [google_project_service.apis["run.googleapis.com"]]

  labels = {{
    environment = var.environment
    app         = var.app_name
  }}
}}

# Allow unauthenticated access (public API)
resource "google_cloud_run_v2_service_iam_member" "public" {{
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}}

# Cloud Storage bucket for static assets
resource "google_storage_bucket" "static" {{
  name     = "${{var.project_id}}-${{var.app_name}}-static"
  location = var.region

  uniform_bucket_level_access = true

  website {{
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }}

  lifecycle_rule {{
    condition {{
      age = 30
    }}
    action {{
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }}
  }}

  labels = {{
    environment = var.environment
    app         = var.app_name
  }}
}}

# Outputs
output "cloud_run_url" {{
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.api.uri
}}

output "static_bucket" {{
  description = "Static assets bucket name"
  value       = google_storage_bucket.static.name
}}

output "service_account" {{
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run.email
}}
"""
