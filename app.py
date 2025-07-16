from flask import Flask
from google.cloud import secretmanager
import os

app = Flask(__name__)

@app.route("/")
def get_secret():
    project_id = os.environ["PROJECT_ID"]
    secret_name = os.environ.get("SECRET_NAME", "db-password")

    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_path})
    secret_value = response.payload.data.decode("UTF-8")

    return f"Secret value: {secret_value}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

