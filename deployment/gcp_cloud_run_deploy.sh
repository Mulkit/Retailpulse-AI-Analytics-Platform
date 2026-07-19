#!/usr/bin/env bash
# RetailPulse — GCP Cloud Run deployment (alternative to AWS ECS Fargate)
#
# Simpler than the Terraform/ECS route above — Cloud Run is a good fit for a
# single-container Streamlit app with no orchestration requirements beyond
# autoscaling. NOT EXECUTED in this environment — no GCP credentials
# available here. Review and run manually with `gcloud auth login` first.

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID first}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="retailpulse-dashboard"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "== Building and pushing image via Cloud Build =="
gcloud builds submit \
  --project "${PROJECT_ID}" \
  --tag "${IMAGE}" \
  --file docker/Dockerfile \
  .

echo "== Deploying to Cloud Run =="
gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --image "${IMAGE}" \
  --platform managed \
  --allow-unauthenticated \
  --port 8501 \
  --cpu 1 \
  --memory 1Gi \
  --min-instances 1 \
  --max-instances 6 \
  --concurrency 40

echo "== Deployment complete =="
gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format "value(status.url)"
