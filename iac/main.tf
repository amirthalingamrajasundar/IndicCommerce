provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_service_account" "service_account" {
  account_id = var.service_account_id
}

resource "google_storage_bucket" "bucket" {
  name     = "indic-commerce"
  location = upper(var.region)
}

resource "google_project_iam_member" "run_sa_gcs_access" {
  bucket = google_storage_bucket.bucket.name
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${data.google_service_account.service_account.email}"
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_cloud_run_service" "app" {
  name     = "indic-commerce"
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        ports {
          container_port = 5000
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
