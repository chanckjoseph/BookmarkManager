#!/bin/bash

# Deployment Script for Bookmark Manager Feasibility Test

set -e  # Exit on error

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null
then
    echo "Error: gcloud CLI is not installed."
    echo "Please install it first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate if needed (basic check)
echo "Checking gcloud authentication..."
gcloud auth list

read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "Project ID cannot be empty."
    exit 1
fi

echo "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "Building container..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/bookmark-feasibility"

echo "Deploying to Cloud Run..."
gcloud run deploy bookmark-feasibility \
  --image "gcr.io/$PROJECT_ID/bookmark-feasibility" \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

echo "Deployment Complete!"
