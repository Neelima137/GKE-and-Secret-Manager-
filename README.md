

#  GKE + Secret Manager Integration with Python App

This project demonstrates how to securely manage secrets in Google Cloud using **Secret Manager** and expose them to a **Python Flask app** deployed on **Google Kubernetes Engine (GKE)** using **Workload Identity**.

---

##  Project Overview

-  Containerized Python app (Flask)
-  Reads secrets from GCP Secret Manager
-  Deployed to GKE using Kubernetes manifests
-  Uses GKE Workload Identity to authenticate with GCP
-  Tagged Docker image with version control
-  No hardcoded credentials — secure and scalable

---

##  Stack

- Python 3.11
- Flask
- Google Cloud Secret Manager
- GKE (Google Kubernetes Engine)
- Docker
- Artifact Registry
- Workload Identity
- `kubectl`, `gcloud`

---

##  Folder Structure

secret/
├── app.py # Flask app
├── requirements.txt # Python deps
├── Dockerfile # Docker build config
├── ksa.yaml # Kubernetes Service Account (linked to GCP SA)
├── deployment.yaml # App Deployment
└── README.md # 📄 You're here


---

## 🚀 How It Works

1. Python app reads a secret from Secret Manager at runtime using the GCP SDK.
2. GKE pod runs with a Kubernetes Service Account.
3. The KSA is mapped to a GCP Service Account via Workload Identity.
4. GCP SA is granted `Secret Manager Accessor` role for the specific secret.
5. No keys, no credentials — just native identity bindings.

---

##  Local Testing

```
export PROJECT_ID=<PROJECT_ID>
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then visit: http://localhost:8080

##  Build & Push Docker Image

docker build -t python-secret-app .
docker tag python-secret-app us-central1-docker.pkg.dev/<PROJECT_ID>/my-repo/python-secret-app:1.0.0
docker push us-central1-docker.pkg.dev/<PROJECT_ID>/my-repo/python-secret-app:1.0.0

Deploy to GKE
1.Enable Workload Identity on the cluster:
```
gcloud container clusters update <cluster-name> \
  --workload-pool=<PROJECT_ID>.svc.id.goog
```
2.Apply KSA and Deployment:
```
kubectl apply -f ksa.yaml
kubectl apply -f deployment.yaml
```
3.Expose the service (optional):
```
kubectl expose deployment python-secret-app \
  --type=LoadBalancer --port=80 --target-port=8080
```
4.Get external IP:
```
kubectl get svc
```

##  Secret Manager Setup

1.Create secret:

```
echo -n "my-db-password" | gcloud secrets create db-password \
  --replication-policy="automatic" --data-file=-

```
2.Create GCP SA and bind secret access:

```
gcloud iam service-accounts create gke-secret-reader
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:gke-secret-reader@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```
3.Annotate KSA with GCP SA:
See ksa.yaml

##  Example Output
When accessing the app:

Secret value: my-db-password

##  Versioning
Images are tagged and stored in Artifact Registry:

```
docker tag python-secret-app:latest ...:1.0.0
gcloud artifacts tags create 1.0.0 ...

```
View tags:
```
gcloud artifacts tags list \
  --location=us-central1 \
  --repository=my-repo \
  --package=python-secret-app \
  --format="table(name, version)"
```


Summary :

How it all works: End-to-End Flow
Step-by-step:
1️ User sends HTTP request → hits the Python app running in GKE.
2️ Python app starts and executes app.py.
3️ App detects the PROJECT_ID and calls Google’s Secret Manager API.
4️ Since the Pod is running with the Kubernetes Service Account (KSA), and KSA is mapped to GSA using Workload Identity, the Pod automatically authenticates to Google Cloud as the GSA.
5️ GSA has roles/secretmanager.secretAccessor → it can read the secret.
6️ Secret Manager returns the secret value.
7️ App sends back a response like:
```
Secret value: my-db-password
```






diagram:

                [ User / Browser ]
                        |
                        v
                +-----------------+
                |   LoadBalancer  |
                +-----------------+
                        |
                        v
            +--------------------------+
            |      GKE Pod             |
            |  Python Flask App        |
            |  (Kubernetes SA: KSA)    |
            +--------------------------+
                        |
                        v
      [Workload Identity: KSA ↔ GSA Binding]
                        |
                        v
            +--------------------------+
            |   Google Service Account |
            |  (gke-secret-reader)     |
            +--------------------------+
                        |
                        v
                +-------------------+
                |  Secret Manager   |
                |  db-password      |
                +-------------------+

WHY?

No credentials are hard-coded.
Secrets are not baked into the Docker image.
Pod identity is secure and auditable.
Follows GCP best practices for GKE + Secret Manager integration.



