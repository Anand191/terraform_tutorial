import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    ScoringProfile,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from loguru import logger

from ai_assistant.utils.global_utils import load_env

load_env()
service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
logger.info(f"Performing index related operations @ {service_endpoint}")
client = SearchIndexClient(service_endpoint, DefaultAzureCredential())


def create_index():
    # [START create_index]
    name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String),
        ComplexField(
            name="address",
            fields=[
                SimpleField(name="streetAddress", type=SearchFieldDataType.String),
                SimpleField(name="city", type=SearchFieldDataType.String),
            ],
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = SearchIndex(
        name=name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options
    )

    client.create_index(index)
    logger.info(f"Created index = {name}")


def get_index():
    # [START get_index]
    name = "hotels"
    client.get_index(name)
    logger.info(f"Retrieved index = {name}")


def update_index():
    # [START update_index]
    name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchableField(name="hotelName", type=SearchFieldDataType.String),
        ComplexField(
            name="address",
            fields=[
                SimpleField(name="streetAddress", type=SearchFieldDataType.String),
                SimpleField(name="city", type=SearchFieldDataType.String),
                SimpleField(name="state", type=SearchFieldDataType.String),
            ],
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(name="MyProfile")
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options
    )

    client.create_or_update_index(index=index)
    logger.info(f"Updated index = {name}")


def delete_index():
    # [START delete_index]
    name = "hotels"
    client.delete_index(name)
    logger.info(f"Deleted index = {name}")


if __name__ == "__main__":
    # create_index()
    # get_index()
    # update_index()
    delete_index()
