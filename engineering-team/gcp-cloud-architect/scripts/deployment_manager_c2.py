# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin2:
    def _gcloud_gke_microservices(self) -> str:
        """Generate gcloud script for GKE microservices pattern."""
        return f"""#!/bin/bash
# GCP GKE Microservices Deployment Script
# Application: {self.app_name}
# Region: {self.region}
# Pattern: GKE Autopilot + Cloud SQL + Memorystore

set -euo pipefail

PROJECT_ID="{self.project_id}"
REGION="{self.region}"
APP_NAME="{self.app_name}"
ENVIRONMENT="${{ENVIRONMENT:-dev}}"
CLUSTER_NAME="${{APP_NAME}}-cluster"
NETWORK_NAME="${{APP_NAME}}-vpc"

echo "=== Deploying $APP_NAME GKE Microservices ($ENVIRONMENT) ==="

# 1. Set project
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \\
  container.googleapis.com \\
  sqladmin.googleapis.com \\
  redis.googleapis.com \\
  cloudbuild.googleapis.com \\
  artifactregistry.googleapis.com \\
  secretmanager.googleapis.com \\
  servicenetworking.googleapis.com \\
  compute.googleapis.com

# 3. Create VPC network
echo "Creating VPC network..."
gcloud compute networks create $NETWORK_NAME \\
  --subnet-mode=auto \\
  || echo "Network already exists"

# Allocate IP range for private services
gcloud compute addresses create google-managed-services-$NETWORK_NAME \\
  --global \\
  --purpose=VPC_PEERING \\
  --prefix-length=16 \\
  --network=$NETWORK_NAME \\
  || echo "IP range already exists"

gcloud services vpc-peerings connect \\
  --service=servicenetworking.googleapis.com \\
  --ranges=google-managed-services-$NETWORK_NAME \\
  --network=$NETWORK_NAME \\
  || echo "VPC peering already exists"

# 4. Create GKE Autopilot cluster
echo "Creating GKE Autopilot cluster..."
gcloud container clusters create-auto $CLUSTER_NAME \\
  --region $REGION \\
  --network $NETWORK_NAME \\
  --release-channel regular \\
  --enable-master-authorized-networks \\
  --enable-private-nodes \\
  || echo "Cluster already exists"

# 5. Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION

# 6. Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $APP_NAME-db \\
  --database-version=POSTGRES_15 \\
  --tier=db-custom-2-8192 \\
  --region=$REGION \\
  --network=$NETWORK_NAME \\
  --no-assign-ip \\
  --availability-type=regional \\
  --backup-start-time=02:00 \\
  --storage-auto-increase \\
  || echo "Cloud SQL instance already exists"

# Create database
gcloud sql databases create $APP_NAME \\
  --instance=$APP_NAME-db \\
  || echo "Database already exists"

# 7. Create Memorystore Redis instance
echo "Creating Memorystore Redis instance..."
gcloud redis instances create $APP_NAME-cache \\
  --size=1 \\
  --region=$REGION \\
  --redis-version=redis_7_0 \\
  --network=$NETWORK_NAME \\
  --tier=basic \\
  || echo "Redis instance already exists"

# 8. Configure Workload Identity
echo "Configuring Workload Identity..."
SA_NAME="${{APP_NAME}}-workload"
gcloud iam service-accounts create $SA_NAME \\
  --display-name="$APP_NAME Workload Identity SA" \\
  || echo "Service account already exists"

gcloud projects add-iam-policy-binding $PROJECT_ID \\
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \\
  --role="roles/cloudsql.client"

gcloud iam service-accounts add-iam-policy-binding \\
  $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com \\
  --role="roles/iam.workloadIdentityUser" \\
  --member="serviceAccount:$PROJECT_ID.svc.id.goog[default/$SA_NAME]"

echo ""
echo "=== GKE Cluster Ready ==="
echo "Cluster: $CLUSTER_NAME"
echo "Cloud SQL: $APP_NAME-db"
echo "Redis: $APP_NAME-cache"
echo ""
echo "Next: Apply Kubernetes manifests with 'kubectl apply -f k8s/'"
"""
