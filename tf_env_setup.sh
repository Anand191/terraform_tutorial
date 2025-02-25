#!/bin/sh

echo "Initialize Env Vars required by Terraform"

# shellcheck source=./secrets/az_sp.config
. ./secrets/az_sp.config

## Export secrets required by terrafrom and az cli as env vars
export ARM_CLIENT_ID="$APP_ID"
export ARM_CLIENT_SECRET="$PASSWORD"
export ARM_TENANT_ID="$TENANT"
export ARM_SUBSCRIPTION_ID="$SUBSCRIPTION"

## Export TF_VAR as env vars
# shellcheck source=./secrets/az_allowed_ip.config
. ./secrets/az_allowed_ip.config

export TF_VAR_local_ip="$LOCAL_IP"
export TF_VAR_static_ip="$STATIC_IP"
export TF_VAR_portal_ip="$PORTAL_IP"
