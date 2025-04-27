# prescriptions/tasks.py

import json
from celery import shared_task
from google.cloud import vision
from google import genai
import requests
from .models import Prescription, Medication
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

# 1) Gemini API 키 설정 (환경변수 또는 .env에 GEN_API_KEY)
genai.Client(api_key=settings.GEN_API_KEY)

@shared_task
def process_prescription(prescription_id):
    # 1) Prescription 인스턴스
    pres = Prescription.objects.get(id=prescription_id)

    # 2) OCR
    client = vision.ImageAnnotatorClient()
    with open(pres.image.path, 'rb') as f:
        image = vision.Image(content=f.read())
    response = client.text_detection(image=image)
    pres.ocr_text = response.full_text_annotation.text
    pres.save(update_fields=['ocr_text'])

    # 3) Gemini에게 파싱 요청
    prompt = f"""
    아래 처방전 텍스트에서 약 이름(name), 1회 투여량(dosage), 1일 투여횟수(frequency)를
    JSON 리스트 형태로 추출해 주세요. 이때 약 이름은 약학정보원에서 제공하는 약품명과 일치해야 합니다.
    약 이름에 투여량, 투여횟수가 포함되면 안됩니다. 예를 들어 한올트리메부틴말레산염/1정이 아니라 한올트리메부틴말레산염만 포함되어야 합니다.

    <<처방전>>
    {pres.ocr_text}

    <<출력 예시>>
    [
        {{"name":"타이레놀","dosage":"1정","frequency":3}},
        {{"name":"판콜에프","dosage":"10ml","frequency":2}}
    ]
    """
    client = genai.Client(api_key=settings.GEN_API_KEY)
    result = client.models.generate_content(
    model="gemini-2.0-flash",    # 사용 가능한 Gemini 모델 이름
    contents=prompt              # 위에서 작성한 프롬프트 문자열
    )
    logger.info("Gemini returned: %s", result.text)
    try:
        meds_data = json.loads(result.text)  # JSON 파싱
    except json.JSONDecodeError:
        meds_data = []

    # 4) 공공약 API 호출 및 DB 저장
    for item in meds_data:
        name     = item.get("name")
        dosage   = item.get("dosage")
        freq     = item.get("frequency", 0)
        # 공공약 API 호출
        r = requests.get(
            "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList",
            params={
                "ServiceKey": settings.OPEN_API_KEY,
                "itemName": name,
                "type": "json",
                "numOfRows": 1,
                "pageNo": 1,
            }
        )
        data = r.json().get("response", {}).get("body", {})
        items = data.get("items", [])
        details = items[0] if items else {}
        Medication.objects.create(
            prescription=pres,
            name=name,
            dosage=dosage,
            frequency_per_day=freq,
            details=details,
        )
