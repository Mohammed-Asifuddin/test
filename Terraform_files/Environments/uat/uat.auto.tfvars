project_id = "Enter Your Project Id"
env        = "uat"
region="us-west1"

topic_name = "btl_video_to_image"
topic_name2 = "startDatastoreExport"
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
  "firebase.googleapis.com",
  "compute.googleapis.com",
  "texttospeech.googleapis.com"

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
  "roles/aiplatform.admin",
  "roles/datastore.importExportAdmin",
  "roles/speech.admin"
]



# substitutions = {
#   _REPO_PROJECT_NAME = "centering-cable-362607"
#   _BRANCH_NAME       = "secret-manager-integration"

# }


repo_links = ["https://github.com/springml-code/btlabel-backend", "https://github.com/springml-code/btlabel-ui", "https://github.com/springml-code/btlabel-admin-ui"]
branchs    = ["develop", "develop", "develop"]
file_paths = ["cloudbuild.yaml", "cloudbuild.yaml", "cloudbuild.yaml"]
repo_names = ["btl-api-service", "btl-user-flow-ui", "btl-admin-ui"]

scheduler_url   = "https://replacewithcloudrunurl/product-training"
scheduler_url2  = "https://replacewithcloudrunurl/backup"
scheduler_freq  = "0 */1 * * *"
scheduler_freq2 = "0 0 * * SUN"


#category_1=["Packaged goods","Toys","Home goods","Apparel","General"]