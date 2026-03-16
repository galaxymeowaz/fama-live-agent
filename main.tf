terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "project-fama"
  region  = "us-central1"
}

# 1. Create a Google Artifact Registry Repository
resource "google_artifact_registry_repository" "fama_repo" {
  location      = "us-central1"
  repository_id = "fama-live-agent-repo"
  description   = "Docker repository for Project Fama."
  format        = "DOCKER"
}

# 2. Provision Google Cloud Run Service (v2)
resource "google_cloud_run_v2_service" "fama_service" {
  name     = "fama-live-agent-service"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/project-fama/fama-live-agent-repo/fama-app:latest"
      
      ports {
        container_port = 8000
      }

      env {
        name  = "PORT"
        value = "8000"
      }
      
      env {
        name  = "JUDGE_PASSCODE"
        value = "famademo2026"
      }

      env {
        name  = "FRIEND_PASSCODE"
        value = "famademo2026"
      }

      env {
        name  = "GEMINI_API_KEY"
        value = "set-via-cloud-console"
      }
      
      env {
        name  = "RECAPTCHA_SECRET_KEY"
        value = "set-via-cloud-console"
      }
    }
  }

  depends_on = [google_artifact_registry_repository.fama_repo]
}

# 3. Grant roles/run.invoker for public access (v2 API)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.fama_service.location
  project  = google_cloud_run_v2_service.fama_service.project
  name     = google_cloud_run_v2_service.fama_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}