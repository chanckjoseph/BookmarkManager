import os
import datetime
from flask import Flask
from google.cloud import firestore

app = Flask(__name__)

# Initialize Firestore client
# Cloud Run injects credentials automatically if the service account has permission.
# Locally, users need GOOGLE_APPLICATION_CREDENTIALS or `gcloud auth application-default login`.
try:
    db = firestore.Client()
    print("Firestore client initialized successfully.")
except Exception as e:
    db = None
    print(f"Warning: Firestore client failed to initialize: {e}")

@app.route("/")
def index():
    if not db:
        return "<h1>Initialization Failed</h1><p>Firestore client could not be created. Check server logs.</p>", 500

    # Write a test document
    # We use a specific collection for this test to avoid polluting real data later
    doc_ref = db.collection("feasibility_tests").document("connectivity_check")
    timestamp = datetime.datetime.now().isoformat()
    
    try:
        # 1. Attempt Write
        doc_ref.set({
            "last_checked": timestamp, 
            "status": "online",
            "message": "Hello from Cloud Run!"
        })
        
        # 2. Attempt Read
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return (
                f"<h1>Feasibility Test: SUCCESS</h1>"
                f"<p><strong>Write & Read Verified.</strong></p>"
                f"<p>Timestamp from Firestore: {data.get('last_checked')}</p>"
                f"<p>Message: {data.get('message')}</p>"
            )
        else:
            return "<h1>Feasibility Test: PARTIAL FAILURE</h1><p>Write seemed successful, but could not read back the document.</p>", 500

    except Exception as e:
        return f"<h1>Feasibility Test: FAILED</h1><p>Firestore Error: {e}</p>", 500

if __name__ == "__main__":
    # Cloud Run sends the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
