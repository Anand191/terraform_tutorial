provider "google" {
    project = "deft-weaver-396616"
    credentials = "${file("./secrets/deft-weaver-396616-9ad20aba844e.json")}"
    region = "europe-west4"
    zone = "europe-west4-a"
}