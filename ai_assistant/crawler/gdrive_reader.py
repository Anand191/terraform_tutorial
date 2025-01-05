import io
import os
import os.path
from datetime import datetime
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from loguru import logger

from ai_assistant.utils.global_utils import load_env

load_env()
project_root = os.environ.get("ROOT")
gcp_project_name = "deft-weaver-396616"
gdrive_creds = os.environ.get("GDRIVE_KEY")
gcs_creds = service_account.Credentials.from_service_account_file(
    os.environ.get("GCS_KEY")
)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_blobs(bucket_name: str, folder_name: str) -> List:
    client = storage.Client(gcp_project_name, gcs_creds)
    bucket = client.get_bucket(bucket_name)
    objects_in_bucket = list(client.list_blobs(bucket))
    folder_objects = [obj.name.endswith("/") for obj in objects_in_bucket]
    folder_names = [x.name[:-1] for x, y in zip(objects_in_bucket, folder_objects) if y]
    if folder_name not in folder_names:
        blob = bucket.blob(f"{folder_name}/")
        blob.upload_from_string("")
        logger.info(f"Created folder {folder_name} in gcs bucket: {bucket_name}")
        return []
    else:
        file_objects = list(client.list_blobs(bucket, prefix=f"{folder_name}/"))
        blob_names = [obj.name for obj in file_objects][1:]
        blob_metadata = [
            datetime.strptime(obj.metadata.get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%fZ")
            for obj in file_objects[1:]
        ]
        blob_timestamps = {
            fname: tstamp for fname, tstamp in zip(blob_names, blob_metadata)
        }
        return (blob_names, blob_timestamps)


def upload_to_gcs(
    bucket_name: str, file_blob: Any, file_name: str, metadata: Dict[str, str]
) -> None:
    client = storage.Client(gcp_project_name, gcs_creds)
    bucket_name = client.get_bucket(bucket_name)
    blob = Blob(file_name, bucket_name)

    # Set blob metadata
    metageneration_match_precondition = None
    # Optional: set a metageneration-match precondition to avoid potential race
    # conditions and data corruptions. The request to patch is aborted if the
    # object's metageneration does not match your precondition.
    metageneration_match_precondition = blob.metageneration
    blob.metadata = metadata
    if metageneration_match_precondition is not None:
        logger.info(metageneration_match_precondition)
        blob.patch(if_metageneration_match=metageneration_match_precondition)
    # Upload to GCS Bucket
    blob.upload_from_file(file_blob, rewind=True)


def delete_from_gcs():
    pass


def _get_revision(service: Any, file_id: str) -> Dict[str, str]:
    response = (
        service.revisions().list(fileId=file_id, fields="*", pageSize=1000).execute()
    )

    revisions = response.get("revisions")
    return revisions[-1]


def get_gdrive_files(bucket_name: str, parent_id: str) -> None:
    """
    Shows basic usage of the Drive v3 API.
    Gets all files in a given drive folder and uploads to
    target GCS bucket
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f"{project_root}/secrets/token.json"):
        creds = Credentials.from_authorized_user_file(
            f"{project_root}/secrets/token.json", SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(gdrive_creds, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f"{project_root}/secrets/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        page_token = None
        objects_list, objects_metadata = get_blobs(bucket_name, parent_id)
        logger.debug(
            f"File: modification timestamp = { {k: v.strftime('%Y-%m-%dT%H:%M:%S.%fZ') for k, v in objects_metadata.items()} }"
        )
        while True:
            # Call the Drive v3 API and get all files from specified parent folder
            results = (
                service.files()
                .list(
                    q=f"mimeType != 'application/vnd.google-apps.folder' and parents in '{parent_id}'",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            items = results.get("files", [])

            if not items:
                logger.info("No files found.")
                return
            # Loop over all found objects and upsert new/modified
            # objects to GCS bucket and delete objects no longer present
            # in drive
            for item in items:
                file_id = item.get("id")
                file_name = f"{parent_id}/{item.get('name')}"
                revision = _get_revision(service, file_id)
                revision_timestamp = datetime.strptime(
                    revision.get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                logger.debug(
                    f"Last revision timestamp for file {file_name} is {revision_timestamp}"
                )
                if (file_name not in objects_list) or (
                    revision_timestamp > objects_metadata.get(file_name)
                ):
                    request = service.files().get_media(fileId=file_id)
                    file_download_buffer = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_download_buffer, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        # print(f"Download {int(status.progress() * 100)}.")
                    upload_to_gcs(
                        bucket_name, file_download_buffer, file_name, metadata=revision
                    )
                    logger.info(
                        f"Found file: {item['name']} ({item['id']}),"
                        f" and (latest version) uploaded to GCS bucket: {bucket_name} and folder: {parent_id}"
                    )
                else:
                    logger.info(
                        f"File: {item['name']} ({item['id']} already exists in gs://{bucket_name}/{parent_id}"
                    )
                # TODO: add deletion from GCS of non-existing files in drive

            page_token = results.get("nextPageToken", None)

            if page_token is None:
                break
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        logger.error(f"An error occurred: {error}")


if __name__ == "__main__":
    folder_id = "1HSiOKkZp6-5lMB1ncEZwTGdrinICXSGQ"
    bucket_name = "pallavi_bucket-1"
    get_gdrive_files(bucket_name=bucket_name, parent_id=folder_id)
