resource "google_project_service" "service" {

  for_each = toset(var.api_enabled_project)

  service = each.key

  project            = var.project_id
  disable_on_destroy = false
}

module "btl_service_account" {
  source       = "../../modules/iam-service-account"
  project_id   = var.project_id
  name         = "btl-${var.env}"
  generate_key = false

  iam_project_roles = {
    "${var.project_id}" = var.iam_permissions_sa_1
  }
}


module "secret-manager" {
  source     = "../../modules/secret-manager"
  project_id = var.project_id
  secrets = {
    user_flow_api_auth   = null
    FIREBASE_WEB_API_KEY = null

  }


  versions = {
    user_flow_api_auth = {

      v1 = { enabled = true, data = "${var.user_flow_api_auth}" }

    },
    FIREBASE_WEB_API_KEY = {

      v1 = { enabled = true, data = "${var.FIREBASE_WEB_API_KEY}" }

    }


  }
  depends_on = [
    google_project_service.service
  ]
}

# resource "google_firebase_project" "btl_firebase" {
#   provider = google-beta
#   project  = var.project_id
#   depends_on = [
#     google_project_service.service
#   ]
# }
resource "random_string" "random" {
  length           = 6
  special          = true
  override_special = "/@£$"
  upper=false
}

resource "google_app_engine_application" "app" {
  project       = var.project_id
  location_id   = var.region
  database_type = "CLOUD_FIRESTORE"
}

resource "google_firestore_document" "config_doc" {
  project    = var.project_id
  collection = "Configuration"
  
  #for_each=toset(local.p)
  
  document_id = "con-${random_string.random.id}"
  fields      = local.conf_field



  # depends_on = [
  #   #google_firebase_project.btl_firebase,
  #   google_app_engine_application.app
  # ]
}

resource "google_firestore_document" "product_doc" {
  project    = var.project_id
  collection = "Product_Category"
  for_each=toset(local.index)
 
  document_id = "prod_col-${each.value}"
  
  fields = jsonencode(
          {
               
          "prd-${each.value}" = {
                   mapValue = {
                       fields = {
                        "category" = {
                               stringValue = "${local.category[tonumber(each.value)]}"
                            },

                           "category_code" = {
                               stringValue = "${local.category_code[tonumber(each.value)]}"
                            },

                          "category_id" = {
                               stringValue = "${local.category_id[tonumber(each.value)]}"
                            },

                          "description"= {
                               stringValue = "${local.description[tonumber(each.value)]}"
                            }
                        
                            
                        }
                    }
                }
            }
        )
  #fields      = "{\"some-doc\":{\"mapValue\":{\"fields\":{\"some_key\":{\"stringValue\":\"value\"},\"some_key2\":{\"stringValue\":\"value2\"}}}}}"

        # for_each=local.prod_fields
        # document_id=each.key
        # dynamic fields = {

        # }


  # depends_on = [
  #   #google_firebase_project.btl_firebase,
  #   google_app_engine_application.app
  # ]
}






resource "google_cloudbuild_trigger" "btl-triggers" {
  count   = length(var.repo_names)
  name    = var.repo_names[count.index]
  project = var.project_id
  source_to_build {
    uri       = "${var.repo_links[count.index]}"
    ref       = "refs/heads/${var.branchs[count.index]}"
    repo_type = "GITHUB"
  }

  git_file_source {
    path      = "${var.file_paths[count.index]}"
    uri       = "${var.repo_links[count.index]}"
    revision  = "refs/heads/${var.branchs[count.index]}"
    repo_type = "GITHUB"
  }
  
  # trigger_template {
  #   branch_name = "${var.branchs[count.index]}"
  #   repo_name   = "${var.repo_names[count.index]}"
  # }
  #substitutions = var.substitutions
  // If this is set on a build, it will become pending when it is run, 
  // and will need to be explicitly approved to start.
  approval_config {
    approval_required = false
  }
  depends_on = [
    google_project_service.service
  ]

}

resource "google_cloud_scheduler_job" "btl_job" {
  name             = "btl_training-${var.env}"
  description      = "http job"
  schedule         = var.scheduler_freq
  time_zone        = var.time_zone
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = var.scheduler_url
    body        = base64encode("{}")
  }
   depends_on = [
    google_project_service.service
  ]
}

resource "google_cloud_scheduler_job" "btl_backup_job" {
  name             = "scheduledDatastoreExport-${var.env}"
  description      = "job for backup"
  schedule         = var.scheduler_freq2
  time_zone        = var.time_zone
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

   pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.btl-backup-topic.id
    data       = base64encode("{\"bucket\":\"gs://${module.Backup_storage.name}\"}")
  }
   depends_on = [
    google_project_service.service,
    google_pubsub_topic.btl-backup-topic
  ]
}

module "Backup_storage" {
  source     = "../../modules/gcs"
  project_id = var.project_id

  name = "${var.project_id}_fire_store_backup"
  #description="bucket to store static files"
  location = "US"
 

}

# resource "google_firebaserules_ruleset" "firestore" {
  
#   source {
#     files {
      
#       content     = var.security_rules
#       name        = "cloud.firestore"
#       fingerprint = sha1(var.security_rules)
#     }
#   }
# }

# resource "google_firebaserules_release" "firestore" {
  
#   name         = "cloud.firestore"
  
#   ruleset_name = google_firebaserules_ruleset.firestore.id
  
# }