provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_service_account" "app_service_account" {
  account_id   = var.app_name
  display_name = "Service Account for ${var.app_name}"
}

resource "google_storage_bucket" "bucket" {
  name     = var.bucket_name
  location = upper(var.region)
}

resource "google_project_iam_member" "firestore_access" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

resource "google_storage_bucket_iam_member" "gcs_access" {
  bucket = google_storage_bucket.bucket.name
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

resource "google_storage_bucket_iam_member" "gcs_public_access" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_cloud_run_service" "app" {
  name     = var.app_name
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.app_service_account.email
      containers {
        image = var.image
        ports {
          container_port = 5000
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "BUCKET_NAME"
          value = google_storage_bucket.bucket.name
        }
        env {
          name  = "SARVAM_API_KEY"
          value = var.sarvam_api_key
        }
        env {
            name = "TWILIO_ACCOUNT_SID"
            value = var.twilio_account_sid
        }
        env {
            name = "TWILIO_AUTH_TOKEN"
            value = var.twilio_auth_token
        }
        env {
            name = "TWILIO_WHATSAPP_NUMBER"
            value = var.twilio_whatsapp_number
        }
        env {
            name = "JOIN_CODE"
            value = var.join_code
        }
        env {
            name = "OPENAI_API_KEY"
            value = var.openai_api_key
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_service.app.location
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_firestore_database" "firestore" {
  name   = var.firestore_database_name
  location_id = var.region
  project = var.project_id
  type   = "FIRESTORE_NATIVE"
}
