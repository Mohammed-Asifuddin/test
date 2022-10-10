locals {
  function_folder1 = "../../../cloud_functions/video_to_image/"
  function_name1   = "btl-cloud-func"
  bucket_name      = "func-${var.project_id}-btl"
  bucket_name2     = "func-backup-${var.project_id}-btl"
  function_folder2 = "../../../cloud_functions/firestore_backup/"
  function_name2   = "btl-backup-cloud-func"
  #bucket_name2 = "${var.project_id}-btl"

}

resource "google_pubsub_topic" "btl-topic" {
  name    = var.topic_name
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
  name    = var.topic_name2
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