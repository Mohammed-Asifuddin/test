
output "email" {
  description = "Service account email."
  value       = local.resource_email_static
  depends_on = [
    local.service_account
  ]
}

output "iam_email" {
  description = "IAM-format service account email."
  value       = local.resource_iam_email_static
  depends_on = [
    local.service_account
  ]
}

output "key" {
  description = "Service account key."
  sensitive   = true
  value       = local.key
}

output "name" {
  description = "Service account id."
  value       = local.service_account.name
}

output "service_account" {
  description = "Service account resource."
  value       = local.service_account
}

output "service_account_credentials" {
  description = "Service account json credential templates for uploaded public keys data."
  value       = local.service_account_credential_templates
}
