resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "random_string" "suffix" {
  length  = 4
  special = false
  upper   = false
}

// RESOURCE GROUP
resource "azurerm_resource_group" "rg" {
  location = var.default_location
  name     = random_pet.rg_name.id
}

data "azurerm_client_config" "current" {}

# VNETS & SUBNETS
# ---------------
// Virtual Network
resource "azurerm_virtual_network" "rg_vnet" {
  name                = "${random_pet.rg_name.id}-vnet"
  address_space       = ["10.1.0.0/24"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

// SUBNET 1
resource "azurerm_subnet" "data_subnet" {
  name                 = "data"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.rg_vnet.name
  address_prefixes     = ["10.1.0.0/27"]
  service_endpoints    = ["Microsoft.Storage", "Microsoft.CognitiveServices"]

  private_endpoint_network_policies = "Enabled"
}

// SUBNET 2
resource "azurerm_subnet" "ai_subnet" {
  name                 = "ai"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.rg_vnet.name
  address_prefixes     = ["10.1.0.32/27"]
  service_endpoints    = ["Microsoft.Storage", "Microsoft.CognitiveServices"]

  private_endpoint_network_policies = "Enabled"
}

# STORAGE ACCOUNT & BLOB CONTAINER
# ---------------------------------
// STORAGE ACCOUNT
resource "azurerm_storage_account" "default" {
  name                            = "${var.prefix}storage${random_string.suffix.result}"
  location                        = azurerm_resource_group.rg.location
  resource_group_name             = azurerm_resource_group.rg.name
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  allow_nested_items_to_be_public = false
}

// NETWORK RULES FOR THE STORAGE CONTAINER
resource "azurerm_storage_account_network_rules" "storage_network_rules" {
  storage_account_id         = azurerm_storage_account.default.id
  default_action             = "Deny"
  ip_rules                   = [var.local_ip, var.static_ip, var.portal_ip]
  virtual_network_subnet_ids = [azurerm_subnet.data_subnet.id]
  bypass                     = ["AzureServices"]
}

// BLOB CONTAINER WIHIN STORAGE ACCOUNT
resource "azurerm_storage_container" "defaultblob" {
  name                  = "${var.prefix}blob${random_string.suffix.result}"
  storage_account_id    = azurerm_storage_account.default.id
  container_access_type = "private"
}

// KEY VAULT
resource "azurerm_key_vault" "defaultkeyvault" {
  name                     = "${var.prefix}keyvault${random_string.suffix.result}"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = false
}

// AZURE AI SEARCH RESOURCE
resource "azurerm_search_service" "defaultsearch" {
  name                         = "${random_pet.rg_name.id}-aisearch"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  sku                          = var.sku
  replica_count                = var.replica_count
  partition_count              = var.partition_count
  local_authentication_enabled = true
  authentication_failure_mode  = "http403"

  public_network_access_enabled = true
  allowed_ips                   = [var.local_ip, var.static_ip, var.portal_ip]
  network_rule_bypass_option    = "AzureServices"
  identity {
    type = "SystemAssigned"
  }
}

# AZURE OPENAI RESOURCE & MODEL DEPLOYMENTS
# -----------------------------------------
// AZURE OPENAI RESOURCE
resource "azurerm_cognitive_account" "openai_resource" {
  name                  = var.openai_deployment
  location              = var.cognitive_services_location
  resource_group_name   = azurerm_resource_group.rg.name
  kind                  = "OpenAI"
  sku_name              = "S0"
  tags                  = var.tags
  custom_subdomain_name = "oai-common-rag"

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
    ip_rules       = [var.local_ip, var.static_ip, var.portal_ip]
  }
}

// OPENAI MODEL DEPLOYMENTS
resource "azurerm_cognitive_deployment" "deployment" {
  for_each             = { for deployment in var.openai_deployments : deployment.name => deployment }
  name                 = each.key
  cognitive_account_id = azurerm_cognitive_account.openai_resource.id
  model {
    format  = "OpenAI"
    name    = each.value.model.name
    version = each.value.model.version
  }

  sku {
    name     = each.value.sku_name
    capacity = each.value.capacity
  }
}

# AI FOUNDRY RELATED
# -----------------
// PROVISIOn AI FOUNDRY HUB
// Azure AI Hub
resource "azapi_resource" "defaulthub" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
  name      = "${random_pet.rg_name.id}-aih"
  location  = var.cognitive_services_location
  parent_id = azurerm_resource_group.rg.id

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      description    = "Sample Azure AI hub"
      friendlyName   = "Sample AI Hub"
      storageAccount = azurerm_storage_account.default.id
      keyVault       = azurerm_key_vault.defaultkeyvault.id

    }
    kind = "hub"
  }
}

// Azure AI Project
resource "azapi_resource" "defaultproject" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
  name      = "ai-project${random_string.suffix.result}"
  location  = var.cognitive_services_location
  parent_id = azurerm_resource_group.rg.id

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      description   = "Sample Azure AI PROJECT"
      friendlyName  = "Sample AI project"
      hubResourceId = azapi_resource.defaulthub.id
    }
    kind = "project"
  }
}

# ALL RBACs
# --------
// MANAGED IDENTITY SCOPED TO BLOB CONTAINER ASSIGNED TO AI SEARCH
resource "azurerm_role_assignment" "rbac_blob_aisearch" {
  role_definition_name = "Storage Blob Data Contributor"
  scope                = azurerm_storage_account.default.id
  principal_id         = azurerm_search_service.defaultsearch.identity[0].principal_id
}

// MANAGED IDENTITY SCOPED TO BLOB CONTAINER ASSIGNED TO OPENAI
resource "azurerm_role_assignment" "rbac_blob_openai" {
  role_definition_name = "Storage Blob Data Contributor"
  scope                = azurerm_storage_account.default.id
  principal_id         = azurerm_cognitive_account.openai_resource.identity[0].principal_id
}

// MANAGED IDENTITY SCOPED TO OPENAI ASSIGNED TO AI SEARCH
resource "azurerm_role_assignment" "rbac_openai_aisearch" {
  role_definition_name = "Cognitive Services OpenAI Contributor"
  scope                = azurerm_cognitive_account.openai_resource.id
  principal_id         = azurerm_search_service.defaultsearch.identity[0].principal_id
}

// MANAGED IDENTITY SCOPED TO AI SEARCH ASSIGNED TO OPENAI
resource "azurerm_role_assignment" "rbac_aisearch_openai" {
  role_definition_name = "Search Service Contributor"
  scope                = azurerm_search_service.defaultsearch.id
  principal_id         = azurerm_cognitive_account.openai_resource.identity[0].principal_id
}

resource "azurerm_role_assignment" "rbac_aisearch_openai_2" {
  role_definition_name = "Search Index Data Reader"
  scope                = azurerm_search_service.defaultsearch.id
  principal_id         = azurerm_cognitive_account.openai_resource.identity[0].principal_id
}

// MANAGED IDENTITY SCOPED TO OPENAI ASSIGNED TO AI FOUNDRY
resource "azurerm_role_assignment" "rbac_openai_aifoundry_hub" {
  role_definition_name = "Cognitive Services User"
  scope                = azurerm_cognitive_account.openai_resource.id
  principal_id         = azapi_resource.defaulthub.identity[0].principal_id
}
