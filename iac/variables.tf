variable "env" {
  description = "The environment for deployment (e.g., dev, prod)"
  type        = string
  default     = "prod"
}

variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
}

variable "app_name" {
  description = "The name of the Cloud Run service"
  type        = string
}

variable "image" {
  description = "The container image to deploy to Cloud Run"
  type        = string
}

variable "db_name" {
  description = "The name of the Firestore database"
  type        = string
}

variable "schema_name" {
  description = "The name of the Firestore schema"
  type        = string
}

variable "bucket_name" {
  description = "The name of the Google Cloud Storage bucket"
  type        = string
}

variable "sarvam_api_key" {
  description = "API key for Sarvam AI"
  type        = string
  sensitive   = true
}

variable "twilio_account_sid" {
  description = "Twilio Account SID"
  type        = string
  sensitive   = true
}

variable "twilio_auth_token" {
  description = "Twilio Auth Token"
  type        = string
  sensitive   = true
}

variable "twilio_whatsapp_number" {
  description = "Twilio WhatsApp Number"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "join_code" {
  description = "Join code for the application"
  type        = string
  sensitive   = true
}