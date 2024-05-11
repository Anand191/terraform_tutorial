GCP_PROJECT_ID=deft-weaver-396616
VERTEX_SA=vertexai-sa@deft-weaver-396616.iam.gserviceaccount.com
TERRAFORM_SA=terraform-sa@deft-weaver-396616.iam.gserviceaccount.com
NEW_ROLE=roles/documentai.editor

vsa_listRoles:
	gcloud projects get-iam-policy ${GCP_PROJECT_ID}  \
	--flatten="bindings[].members" \
	--format='table(bindings.role)' \
	--filter="bindings.members:${VERTEX_SA}"

tf_listRoles:
	gcloud projects get-iam-policy ${GCP_PROJECT_ID}  \
	--flatten="bindings[].members" \
	--format='table(bindings.role)' \
	--filter="bindings.members:${TERRAFORM_SA}"

vsa_assignRole:
	gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
    --member=serviceAccount:${VERTEX_SA} \
    --role=${NEW_ROLE}

