from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage

TEMP_STORAGE_ROOT = "temp_files/"


def select_storage():
    """
    Utility method to select the storage type based on where the application is run.
    When deploying to AWS, We need to set the S3_STORAGE_ENABLED to true by setting the environment variable
    with the same name.
    :return:
    """
    return S3Boto3Storage(location=TEMP_STORAGE_ROOT) if settings.S3_STORAGE_ENABLED else FileSystemStorage()


def s3_root_storage():
    """
    Storage instance that allows access from the root level on S3
    :return:
    """
    return S3Boto3Storage()
