terraform {
  backend "gcs" {
    #Enter Your Bucket Name> for storing state file
    bucket = "<Enter Your Bucket Name>"
    prefix = "terraform-state"
  }
}