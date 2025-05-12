# core/utils.py

from google.cloud import storage
import uuid

def upload_image_to_gcs(django_file, file_name=None):
    client = storage.Client()
    bucket = client.bucket("medsafe-rx-images")

    # 고유한 파일 이름 생성
    ext = django_file.name.split('.')[-1]
    file_name = file_name or f"{uuid.uuid4()}.{ext}"

    blob = bucket.blob(file_name)
    blob.upload_from_file(django_file, content_type=django_file.content_type)

    # 공개 읽기 권한 부여
    blob.make_public()

    return blob.public_url