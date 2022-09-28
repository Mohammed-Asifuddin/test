terraform {
  backend "gcs" {
    bucket = "<Enter Bucket Name>"
    prefix = "terraform-state"
  }
}