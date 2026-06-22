# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin3:
    def _gcloud_data_pipeline(self) -> str:
        """Generate gcloud script for data pipeline pattern."""
        return f"""#!/bin/bash
# GCP Data Pipeline Deployment Script
# Application: {self.app_name}
# Region: {self.region}
# Pattern: Pub/Sub + Dataflow + BigQuery

set -euo pipefail

PROJECT_ID="{self.project_id}"
REGION="{self.region}"
APP_NAME="{self.app_name}"

echo "=== Deploying $APP_NAME Data Pipeline ==="

# 1. Set project
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \\
  pubsub.googleapis.com \\
  dataflow.googleapis.com \\
  bigquery.googleapis.com \\
  storage.googleapis.com \\
  monitoring.googleapis.com

# 3. Create Pub/Sub topic and subscription
echo "Creating Pub/Sub resources..."
gcloud pubsub topics create $APP_NAME-events \\
  || echo "Topic already exists"

gcloud pubsub subscriptions create $APP_NAME-events-sub \\
  --topic=$APP_NAME-events \\
  --ack-deadline=60 \\
  --message-retention-duration=7d \\
  || echo "Subscription already exists"

# Dead letter topic
gcloud pubsub topics create $APP_NAME-events-dlq \\
  || echo "DLQ topic already exists"

gcloud pubsub subscriptions update $APP_NAME-events-sub \\
  --dead-letter-topic=$APP_NAME-events-dlq \\
  --max-delivery-attempts=5

# 4. Create BigQuery dataset and table
echo "Creating BigQuery resources..."
bq mk --dataset --location=$REGION $PROJECT_ID:${{APP_NAME//-/_}}_analytics \\
  || echo "Dataset already exists"

bq mk --table \\
  $PROJECT_ID:${{APP_NAME//-/_}}_analytics.events \\
  event_id:STRING,event_type:STRING,payload:STRING,timestamp:TIMESTAMP,processed_at:TIMESTAMP \\
  --time_partitioning_type=DAY \\
  --time_partitioning_field=timestamp \\
  --clustering_fields=event_type \\
  || echo "Table already exists"

# 5. Create Cloud Storage bucket for Dataflow temp/staging
echo "Creating staging bucket..."
STAGING_BUCKET="${{PROJECT_ID}}-${{APP_NAME}}-dataflow"
gsutil mb -l $REGION gs://$STAGING_BUCKET/ || echo "Bucket already exists"

# 6. Create service account for Dataflow
echo "Creating Dataflow service account..."
SA_NAME="${{APP_NAME}}-dataflow-sa"
gcloud iam service-accounts create $SA_NAME \\
  --display-name="$APP_NAME Dataflow Worker SA" \\
  || echo "Service account already exists"

for ROLE in roles/dataflow.worker roles/bigquery.dataEditor roles/pubsub.subscriber roles/storage.objectAdmin; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \\
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \\
    --role="$ROLE" \\
    --condition=None
done

echo ""
echo "=== Data Pipeline Infrastructure Ready ==="
echo "Pub/Sub Topic: $APP_NAME-events"
echo "BigQuery Dataset: ${{APP_NAME//-/_}}_analytics"
echo "Staging Bucket: gs://$STAGING_BUCKET"
echo ""
echo "Next: Deploy Dataflow job with Apache Beam pipeline"
echo "  python -m apache_beam.examples.streaming_wordcount \\\\"
echo "    --runner DataflowRunner \\\\"
echo "    --project $PROJECT_ID \\\\"
echo "    --region $REGION \\\\"
echo "    --temp_location gs://$STAGING_BUCKET/temp"
"""
    def generate_terraform_configuration(self) -> str:
        """
        Generate Terraform configuration for the selected pattern.

        Returns:
            Terraform HCL configuration as string
        """
        if self.pattern == 'serverless_web':
            return self._terraform_serverless_web()
        elif self.pattern == 'gke_microservices':
            return self._terraform_gke_microservices()
        else:
            return self._terraform_serverless_web()
