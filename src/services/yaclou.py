import boto3

from core.config import app_settings


class YObjectStorage:
    def __init__(self, bucket_name: str):
        self.session = boto3.session.Session()
        self.s3 = self.session.client(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
        self.bucket_name = bucket_name

    def store_bytes(self, body: bytes, id: str) -> None:
        self.s3.put_object(Bucket=self.bucket_name, Key=id, Body=body, StorageClass='STANDARD')

    def store_file(self, file_name: str, id: str) -> None:
        self.s3.upload_file(file_name, self.bucket_name, id)

    def get_file(self, id: str) -> bytes:
        get_object_response = self.s3.get_object(Bucket=self.bucket_name, Key=id)
        return get_object_response['Body'].read()

    def get_content_list(self) -> list:
        return [key['Key'] for key in self.s3.list_objects(Bucket=self.bucket_name)['Contents']]


yos = YObjectStorage(app_settings.YA_BUCKET_NAME)
