terraform {
  backend "gcs" {
    bucket = "btl-test-4"
    prefix = "terraform-state"
  }
}