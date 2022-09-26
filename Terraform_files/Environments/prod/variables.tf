variable "project_id" {
  description = "Identifier of the project."
  type        = string


}
variable "env" {
  description = "env used for created resources."
  type        = string

}
variable "region" {
  description = "Region used for regional resources."
  type        = string
  default     = "us-west1"
}
variable "api_enabled_project" {
  type        = list(string)
  description = "Apis needs to be enabled for project"
}

variable "iam_permissions_sa_1" {
  type        = list(string)
  description = "List of IAM Permissons"
}
variable "user_flow_api_auth" {
  description = "secret value for userflow."
  type        = string
  default     = "null"
}
variable "FIREBASE_WEB_API_KEY" {
  description = "Secret value for firebase."
  type        = string
  default     = "null"
}

variable "topic_name" {
  description = "Pubsub topic name."
  type        = string
  
}
variable "time_zone" {
  description = "Timezone Name."
  type        = string
  
}
variable "scheduler_url" {
  description = "Url for Scheduler."
  type        = string
  
}
variable "scheduler_freq" {
  description = "Frequency for Scheduler."
  type        = string
  
}



variable "repo_names" {
  description = "Cloud build names"
  type        = list(string)
  #default = "btl-backend-build"
}

variable "repo_links" {
  description = "Github link for the repos"
  type        = list(string)

}

variable "file_paths" {
  description = "yaml file paths"
  type        = list(string)
}

variable "branchs" {
  description = "branches to build"
  type        = list(string)

}

variable "substitutions" {
  description = "Variable substitutions for cloud build"
  default     = null

}


variable "fields_x" {
    description = "field details"
    default = {
      "fields" = {
         "stringValue" = "xyz"
      }
    }
}
