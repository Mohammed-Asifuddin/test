terraform {
  backend "gcs" {
    bucket = "mystate-26-09"
    prefix = "terraform-state"
  }
}