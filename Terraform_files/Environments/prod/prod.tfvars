project_id = "Enter Your Project-id"
region="us-west1"
topic_name = "btl_video_to_image"
time_zone = "America/Los_Angeles"
api_enabled_project = [
  "cloudfunctions.googleapis.com",
  "pubsub.googleapis.com",
  "iam.googleapis.com",
  "iamcredentials.googleapis.com",
  "vision.googleapis.com",
  "storage.googleapis.com",
  "cloudscheduler.googleapis.com",
  "secretmanager.googleapis.com",
  "cloudbuild.googleapis.com",
  "dialogflow.googleapis.com",
  "run.googleapis.com",
  "firestore.googleapis.com",
  "firebase.googleapis.com"

]
iam_permissions_sa_1 = [
  "roles/cloudfunctions.admin",
  "roles/secretmanager.admin",
  "roles/artifactregistry.writer",
  "roles/cloudbuild.builds.editor",
  "roles/run.admin",
  "roles/cloudscheduler.admin",
  "roles/dialogflow.admin",
  "roles/firebase.admin",
  "roles/pubsub.admin",
  "roles/iam.serviceAccountTokenCreator",
  "roles/serviceusage.serviceUsageConsumer",
  "roles/storage.admin",
  "roles/logging.logWriter",
  "roles/iam.serviceAccountUser",
  "roles/aiplatform.admin"
]



# substitutions = {
#   _REPO_PROJECT_NAME = "centering-cable-362607"
#   _BRANCH_NAME       = "secret-manager-integration"

# }

env        = "prod"

repo_links = ["https://github.com/springml-code/btlabel-backend", "https://github.com/springml-code/btlabel-ui", "https://github.com/springml-code/btlabel-ui"]
branchs    = ["secret-manager-integration", "btl-client", "varun-angular-updation"]
file_paths = ["cloudbuild.yaml", "cloudbuild.yaml", "btl-adminscreen-ui/cloudbuild.yaml"]
repo_names = ["btl-backend-trigger", "btl-client-ui-trigger", "btl-admin-ui-trigger"]

scheduler_url = "https://replacewithcloudrunurl/product-training"
scheduler_freq = "0 */1 * * *"