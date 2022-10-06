locals {
function_folder1 = "../../../cloud_functions/video_to_image/"
function_name1   = "btl-cloud-func"
bucket_name = "func-${var.project_id}-btl"
bucket_name2 = "func-backup-${var.project_id}-btl"
function_folder2 = "../../../cloud_functions/firestore_backup/"
function_name2   = "btl-backup-cloud-func"
#bucket_name2 = "${var.project_id}-btl"

}
# resource "google_cloudfunctions_function" "function" {
#   name        = local.function_name
#   description = "processing"
#   runtime     = "python39"
#   region      = var.region

#   available_memory_mb   = 128
#   source_archive_bucket = google_storage_bucket.source.name
#   source_archive_object = google_storage_bucket_object.archive.name

#     event_trigger  {
#     event_type = "google.pubsub.topic.publish"
#     resource = "projects/${var.project_id}/topics/${google_pubsub_topic.btl-sample.id}"
#     failure_policy {
#       retry=true
#     }
#   }
#   entry_point           = "video_to_image"


#   depends_on = [google_project_service.service]
# }

# # A dedicated Cloud Storage bucket to store the zip source
# resource "google_storage_bucket" "source" {

#   name = "${var.project_id}-source"
#   location="US"
# }

# # Create a fresh archive of the current function folder
# data "archive_file" "function" {
#   type        = "zip"
#   output_path = "temp/function_code_${timestamp()}.zip"
#   source_dir  = local.function_folder
#   output_file_mode = "0666"
# }

# # The archive in Cloud Stoage uses the md5 of the zip file
# # This ensures the Function is redeployed only when the source is changed.
# resource "google_storage_bucket_object" "archive" {
#   name = "${local.function_folder}_${data.archive_file.function.output_md5}.zip" # will delete old items

#   bucket = google_storage_bucket.source.name
#   source = data.archive_file.function.output_path

#   depends_on = [data.archive_file.function]
# }
resource "google_pubsub_topic" "btl-topic" {
  name    = "${var.topic_name}"
  project = var.project_id


  message_retention_duration = "86600s"
}


module "cloud-func-btl" {
  source      = "../../modules/cloud-function"
  project_id  = var.project_id
  name        = local.function_name1
  region      = var.region
  bucket_name = local.bucket_name
  bucket_config = {
    location             = "US"
    lifecycle_delete_age = 1
  }
  bundle_config = {
    source_dir  = local.function_folder1
    output_path = "temp/bundle.zip"
    excludes    = null
  }
  function_config = {
    entry_point = "video_to_image"
    instances   = 1
    memory      = 256
    runtime     = "python39"
    timeout     = 180
  }
  trigger_config = {
    event    = "google.pubsub.topic.publish"
    resource = google_pubsub_topic.btl-topic.name
    retry    = true
  }
   depends_on = [google_pubsub_topic.btl-topic,
  google_project_service.service
    
  ]
}

resource "google_pubsub_topic" "btl-backup-topic" {
  name    = "${var.topic_name2}"
  project = var.project_id


  message_retention_duration = "86600s"
}


module "cloud-func-backup-btl" {
  source      = "../../modules/cloud-function"
  project_id  = var.project_id
  name        = local.function_name2
  region      = var.region
  bucket_name = local.bucket_name2
  bucket_config = {
    location             = "US"
    lifecycle_delete_age = 1
  }
  bundle_config = {
    source_dir  = local.function_folder2
    output_path = "temp/backup_bundle.zip"
    excludes    = null
  }
  function_config = {
    entry_point = "datastore_export"
    instances   = 1
    memory      = 256
    runtime     = "python39"
    timeout     = 180
  }
  trigger_config = {
    event    = "google.pubsub.topic.publish"
    resource = google_pubsub_topic.btl-backup-topic.name
    retry    = true
  }
  depends_on = [google_pubsub_topic.btl-backup-topic,
  google_project_service.service
    
  ]
}