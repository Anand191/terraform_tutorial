provider "google" {
    project = var.project
    credentials = file(var.credentials)
    region = var.region
    zone = var.zone
}

resource "google_compute_network" "terraform_network" {
    name = var.network_params.name
    auto_create_subnetworks = var.network_params.auto_create_subnetworks
}

resource "google_compute_subnetwork" "terraform_subnet" {
    name = var.subnet_params.name
    ip_cidr_range = var.subnet_params.ip_cidr_range
    region = var.region
    network = google_compute_network.terraform_network.id
}

resource "google_compute_instance" "sample_compute_instance" {
    name = var.vm_params.name
    machine_type = var.vm_params.machine_type
    zone = var.zone
    allow_stopping_for_update = var.vm_params.allow_stopping_for_update
    boot_disk {
        initialize_params {
          image = var.os_image
        }
      
    }
    network_interface {
      network = google_compute_network.terraform_network.self_link
      subnetwork = google_compute_subnetwork.terraform_subnet.self_link
      access_config {
        // necessary even empty
      }
    }

}