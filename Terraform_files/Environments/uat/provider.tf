terraform {
  required_version = ">= 1.1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.17.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 4.17.0"
    }
  }
}


provider "google-beta" {
  project = var.project_id
  region  = var.region

  #credentials = file("C://Users/SpringML/Desktop/Projects/my-beta-key.json")
}

provider "google" {
  project = var.project_id
  region  = var.region
  #credentials = file("C://Users/SpringML/Desktop/Projects/my-beta-key.json")
}
provider "random" {

}