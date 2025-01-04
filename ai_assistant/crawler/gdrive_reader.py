import io
import os
import os.path
from typing import List

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
        return [obj.name for obj in file_objects][1:]


def upload_to_gcs(
    bucket_name: str, file_blob: MediaIoBaseDownload, file_name: str
) -> None:
    client = storage.Client(gcp_project_name, gcs_creds)
    bucket_name = client.get_bucket(bucket_name)
    blob = Blob(file_name, bucket_name)
    blob.upload_from_file(file_blob, rewind=True)


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
        objects_list = get_blobs(bucket_name, parent_id)

        while True:
            # Call the Drive v3 API
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

            for item in items:
                file_id = item.get("id")
                file_name = f"{parent_id}/{item.get('name')}"
                if file_name not in objects_list:
                    request = service.files().get_media(fileId=file_id)
                    file_download_buffer = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_download_buffer, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        # print(f"Download {int(status.progress() * 100)}.")
                    upload_to_gcs(bucket_name, file_download_buffer, file_name)
                    logger.info(
                        f"Found file: {item['name']} ({item['id']}),"
                        f" and uploaded to GCS bucket: {bucket_name} and folder: {parent_id}"
                    )
                else:
                    logger.info(
                        f"File: {item['name']} ({item['id']} already exists in gs://{bucket_name}/{parent_id}"
                    )

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
