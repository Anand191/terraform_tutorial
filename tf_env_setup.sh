#!/bin/sh

echo "Initialize Env Vars required by Terraform"

# shellcheck source=./secrets/az_sp.config
. ./secrets/az_sp.config

## Export as env vars
export ARM_CLIENT_ID="$APP_ID"
export ARM_CLIENT_SECRET="$PASSWORD"
export ARM_TENANT_ID="$TENANT"
export ARM_SUBSCRIPTION_ID="$SUBSCRIPTION"
