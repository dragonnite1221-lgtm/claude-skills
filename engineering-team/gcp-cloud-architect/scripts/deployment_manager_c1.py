# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin1:
    def _gcloud_serverless_web(self) -> str:
        """Generate gcloud script for serverless web pattern."""
        return f"""#!/bin/bash
# GCP Serverless Web Deployment Script
# Application: {self.app_name}
# Region: {self.region}
# Pattern: Cloud Run + Firestore + Cloud Storage + Cloud CDN

set -euo pipefail

PROJECT_ID="{self.project_id}"
REGION="{self.region}"
APP_NAME="{self.app_name}"
ENVIRONMENT="${{ENVIRONMENT:-dev}}"

echo "=== Deploying $APP_NAME to GCP ($ENVIRONMENT) ==="

# 1. Set project
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \\
  run.googleapis.com \\
  firestore.googleapis.com \\
  cloudbuild.googleapis.com \\
  artifactregistry.googleapis.com \\
  secretmanager.googleapis.com \\
  compute.googleapis.com \\
  monitoring.googleapis.com \\
  logging.googleapis.com

# 3. Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create $APP_NAME \\
  --repository-format=docker \\
  --location=$REGION \\
  --description="Docker images for $APP_NAME" \\
  || echo "Repository already exists"

# 4. Build and push container image
echo "Building container image..."
gcloud builds submit \\
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/$APP_NAME/$APP_NAME:latest \\
  .

# 5. Create Firestore database
echo "Creating Firestore database..."
gcloud firestore databases create \\
  --location=$REGION \\
  --type=firestore-native \\
  || echo "Firestore database already exists"

# 6. Create service account for Cloud Run
echo "Creating service account..."
SA_NAME="${{APP_NAME}}-run-sa"
gcloud iam service-accounts create $SA_NAME \\
  --display-name="$APP_NAME Cloud Run Service Account" \\
  || echo "Service account already exists"

# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \\
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \\
  --role="roles/datastore.user" \\
  --condition=None

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \\
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \\
  --role="roles/secretmanager.secretAccessor" \\
  --condition=None

# 7. Deploy Cloud Run service
echo "Deploying Cloud Run service..."
gcloud run deploy $APP_NAME-api \\
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$APP_NAME/$APP_NAME:latest \\
  --region $REGION \\
  --platform managed \\
  --service-account $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com \\
  --memory 512Mi \\
  --cpu 1 \\
  --min-instances 0 \\
  --max-instances 10 \\
  --set-env-vars "PROJECT_ID=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT" \\
  --allow-unauthenticated

# 8. Create Cloud Storage bucket for static assets
echo "Creating static assets bucket..."
BUCKET_NAME="${{PROJECT_ID}}-${{APP_NAME}}-static"
gsutil mb -l $REGION gs://$BUCKET_NAME/ || echo "Bucket already exists"
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# 9. Set up Cloud Monitoring alerting
echo "Setting up monitoring..."
gcloud alpha monitoring policies create \\
  --notification-channels="" \\
  --display-name="$APP_NAME High Error Rate" \\
  --condition-display-name="Cloud Run 5xx Error Rate" \\
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"' \\
  --condition-threshold-value=10 \\
  --condition-threshold-duration=60s \\
  || echo "Alert policy creation requires additional configuration"

# 10. Output deployment info
echo ""
echo "=== Deployment Complete ==="
SERVICE_URL=$(gcloud run services describe $APP_NAME-api --region $REGION --format 'value(status.url)')
echo "Cloud Run URL: $SERVICE_URL"
echo "Static Bucket: gs://$BUCKET_NAME"
echo "Firestore: https://console.cloud.google.com/firestore?project=$PROJECT_ID"
echo "Monitoring: https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
"""
