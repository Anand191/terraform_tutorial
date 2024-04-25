variable "project" {}
variable "credentials" {}

variable "region" {
    default = "europe-west4"
}

variable "zone" {
    default = "europe-west4-a"
}

variable "os_image" {
    default = "debian-cloud/debian-11"

}

variable "vm_params" {
    type = object({
      name = string
      machine_type = string
      allow_stopping_for_update = bool
    })
    description = "vm parameters"
    default = {
      name = "sample-vm-instance"
      machine_type = "f1-micro"
      allow_stopping_for_update = true
    }

    validation {
      condition = length(var.vm_params.name) > 4
      error_message = "VM name must be at least 5 characters"
    }
}

variable "network_params" {
    type = object({
        name = string
        auto_create_subnetworks = bool
    })
    description = "network parameters"
    default = {
      name = "terraform-network"
      auto_create_subnetworks = false
    }
}

variable "subnet_params" {
    type = object({
        name = string
        ip_cidr_range = string
    })
    description = "subnet parameters"
    default = {
      name = "terraform-subnet"
      ip_cidr_range = "10.20.0.0/16"
    }
}