variable "default_location" {
  type        = string
  default     = "westeurope"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  type        = string
  default     = "rg"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "prefix" {
  type        = string
  description = "This variable is used to name the hub, project, and dependent resources."
  default     = "ai"
}

variable "sku" {
  description = "The pricing tier of the search service you want to create (for example, basic or standard)."
  default     = "standard"
  type        = string
  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], var.sku)
    error_message = "The sku must be one of the following values: free, basic, standard, standard2, standard3, storage_optimized_l1, storage_optimized_l2."
  }
}

variable "replica_count" {
  type        = number
  description = "Replicas distribute search workloads across the service. You need at least two replicas to support high availability of query workloads (not applicable to the free tier)."
  default     = 1
  validation {
    condition     = var.replica_count >= 1 && var.replica_count <= 12
    error_message = "The replica_count must be between 1 and 12."
  }
}

variable "partition_count" {
  type        = number
  description = "Partitions allow for scaling of document count as well as faster indexing by sharding your index over multiple search units."
  default     = 1
  validation {
    condition     = contains([1, 2, 3, 4, 6, 12], var.partition_count)
    error_message = "The partition_count must be one of the following values: 1, 2, 3, 4, 6, 12."
  }
}

variable "openai_deployment" {
  type        = string
  description = "Name of the Open Ai resource deployment"
  default     = "openai_common"
}

variable "openai_deployments" {
  description = "(Optional) Specifies the deployments of the Azure OpenAI Service"
  type = list(object({
    name = string
    model = object({
      name    = string
      version = string
    })
    rai_policy_name = string
    sku_name        = string
    capacity        = number
  }))
  default = [
    {
      name = "chatmodel-4o-mini"
      model = {
        name    = "gpt-4o-mini"
        version = "2024-07-18"
      }
      rai_policy_name = "Microsoft.DefaultV2"
      sku_name        = "GlobalStandard"
      capacity        = 30
    },
    {
      name = "embedding-small"
      model = {
        name    = "text-embedding-3-small"
        version = "1"
      }
      rai_policy_name = "Microsoft.DefaultV2"
      sku_name        = "Standard"
      capacity        = 350
    }
  ]
}

variable "tags" {
  description = "(Optional) Specifies tags for all the resources"
  default = {
    createdWith = "Terraform"
  }
}
