# prescriptions/tasks.py

from celery import shared_task
from google.cloud import vision
import requests
from .models import Prescription, Medication
from django.conf import settings

@shared_task
def process_prescription(prescription_id):
    # 1) Prescription 인스턴스 가져오기
    pres = Prescription.objects.get(id=prescription_id)

    # 2) Google Vision OCR 실행
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    with open(pres.image.path, 'rb') as f:
        image.content = f.read()
    response = client.text_detection(image=image)
    pres.ocr_text = response.full_text_annotation.text
    pres.save(update_fields=['ocr_text'])

    # 3) OCR 텍스트에서 약 이름·횟수·용량 파싱 (간단 예시)
    #    실제로는 정규표현식·NLP 등을 써서 더 견고히 만드세요.
    lines = pres.ocr_text.splitlines()
    meds = []
    for line in lines:
        if '정' in line or 'ml' in line:
            # 예시: “타이레놀 1정 3회” 형식
            parts = line.split()
            name, dosage, freq = parts[0], parts[1], int(parts[2].replace('회',''))
            meds.append((name, dosage, freq))

    # 4) 공공약 API 호출로 상세정보 가져오기
    for name, dosage, freq in meds:
        r = requests.get(
            f'https://api.odcloud.kr/api/15077603/v1/uddi:XXXXXXXXXX',
            params={'serviceKey': settings.OPEN_API_KEY, 'itemName': name}
        )
        details = r.json().get('data', [{}])[0]
        Medication.objects.create(
            prescription=pres,
            name=name,
            dosage=dosage,
            frequency_per_day=freq,
            details=details,
        )
