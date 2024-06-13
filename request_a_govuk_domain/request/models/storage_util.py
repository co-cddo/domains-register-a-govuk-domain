from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


def select_storage():
    """
    Utility method to select the storage type based on where the application is run.
    When deploying to AWS, We need to set the IS_AWS to true by setting the environment variable
    with the same name.
    :return:
    """
    return S3Boto3Storage() if settings.S3_STORAGE_ENABLED else FileSystemStorage()
