# Feasibility Test: Cloud Run + Firestore

This prototype verifies:
1.  Deployment to Google Cloud Run.
2.  Connectivity to Google Cloud Firestore (Read/Write).

## Prerequisites
You need the `gcloud` CLI installed and authenticated.

1.  **Install gcloud**: [Follow Google's Instructions](https://cloud.google.com/sdk/docs/install)
2.  **Login**:
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```
3.  **Enable APIs**:
    Ensure Cloud Run and Firestore APIs are enabled in your project.

## How to Deploy

Run the following commands from this directory:

```bash
# 1. Build and Submit the Container to Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bookmark-feasibility

# 2. Deploy to Cloud Run
gcloud run deploy bookmark-feasibility \
  --image gcr.io/YOUR_PROJECT_ID/bookmark-feasibility \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
*(Replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID)*

## How to Test Locally
To run locally, you need application-default credentials:

```bash
# 1. Acquire credentials
gcloud auth application-default login

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```
Then visit `http://localhost:8080`.
