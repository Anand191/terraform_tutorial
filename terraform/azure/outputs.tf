output "resource_group_name" {

  description = "The name of the created resource group."
  value       = azurerm_resource_group.rg.name
}

output "virtual_network_name" {
  description = "The name of the created virtual network."
  value       = azurerm_virtual_network.rg_vnet.name
}

output "subnet_1_name" {
  description = "The name of the created subnet 1."
  value       = azurerm_subnet.data_subnet.name
}

output "subnet_2_name" {
  description = "The name of the created subnet 2."
  value       = azurerm_subnet.ai_subnet.name
}

output "storage_account_name" {
  description = "The name of the created storage account"
  value       = azurerm_storage_account.default.name
}

output "azurerm_search_service_name" {
  description = "The name of the created ai search resource"
  value       = azurerm_search_service.defaultsearch.name
}

output "azurerm_openai_resource_name" {
  description = "The name of the created openai resource"
  value       = azurerm_cognitive_account.openai_resource.name
}
