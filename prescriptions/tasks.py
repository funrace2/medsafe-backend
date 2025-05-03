# prescriptions/tasks.py

import json
import difflib
from urllib.parse import unquote
from celery import shared_task
from google.cloud import vision
from google import genai
import requests
from .models import Prescription, Medication
from django.conf import settings
# from core.firebase import send_push
import logging
logger = logging.getLogger(__name__)

# .env에서 불러온 원본 키
raw_key = settings.OPEN_API_KEY
# URL 디코딩
decoded_key = unquote(raw_key)

@shared_task
def process_prescription(prescription_id):
    # 1) Prescription 인스턴스
    pres = Prescription.objects.get(id=prescription_id)

    # 1) Gemini API 키 설정 (환경변수 또는 .env에 GEN_API_KEY)
    genai.Client(api_key=settings.GEN_API_KEY)

    # 2) OCR
    client = vision.ImageAnnotatorClient()
    with open(pres.image.path, 'rb') as f:
        image = vision.Image(content=f.read())
    response = client.text_detection(image=image)
    pres.ocr_text = response.full_text_annotation.text
    pres.save(update_fields=['ocr_text'])

    # 3) Gemini에게 파싱 요청
    prompt = f"""
    아래 처방전 또는 약봉투 텍스트에서 약 이름(name), 1회 투여량(dosage), 1일 투여횟수(frequency), 약국 이름(pharmacy_name), 약국 전화번호(pharmacy_phone), 병원 이름(hospital_name)을
    JSON 리스트 형태로 추출해 주세요. 이때 약 이름은 약학정보원에서 제공하는 약품명과 일치해야 합니다.
    약 이름에 투여량, 투여횟수가 포함되면 안됩니다. 예를 들어 한올트리메부틴말레산염/1정이 아니라 한올트리메부틴말레산염만 포함되어야 합니다.
    약국 이름에는 "약국"이라는 단어가 포함되어야 합니다.

    <<처방전>>
    {pres.ocr_text}

    <<출력 예시>>
    [
        {{"name":"타이레놀","dosage":"1정","frequency":3,"pharmacy_name":"가나다약국","pharmacy_phone":"02-123-4567","hospital_name":"서울중앙병원"}},
        {{"name":"판콜에프","dosage":"10ml","frequency":2,"pharmacy_name":"라마바약국","pharmacy_phone":"032-987-7654","hospital_name":"인천중앙병원"}}
    ]
    """
    client = genai.Client(api_key=settings.GEN_API_KEY)
    result = client.models.generate_content(
    model="gemini-2.0-flash",    # 사용 가능한 Gemini 모델 이름
    contents=prompt              # 위에서 작성한 프롬프트 문자열
    )
    raw = result.text
    logger.info("🛠 Gemini returned raw text:\n%s", raw)

    # --- Markdown fenced code block 제거 ---
    # ```json\n ... \n```
    if raw.startswith("```"):
        # 첫 줄 ```json 제거
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        # 마지막 ``` 제거
        raw = raw.rsplit("\n", 1)[0]

    try:
        meds_data = json.loads(raw)  # 깔끔해진 JSON 문자열로 파싱
    except json.JSONDecodeError:
        logger.error("❌ JSONDecodeError parsing cleaned result: %r", raw)
        meds_data = []

    logger.info("🔍 Parsed meds_data (%d items): %r", len(meds_data), meds_data)

    # 4) 공공약 API 호출 및 DB 저장
    for item in meds_data:
        name   = item.get("name")
        dosage = item.get("dosage")
        freq   = item.get("frequency", 0)

        # e약은요 서비스 호출
        resp = requests.get(
            "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList",
            params={
                "ServiceKey": decoded_key,  # URL 디코딩된 키
                "itemName": name,       # 처방전에서 추출한 약 이름
                "type": "json",
                "numOfRows": 20,
                "pageNo": 1,
            }
        )
        logger.info("API 상태: %s, 본문: %s", resp.status_code, resp.text)

        resp_json = resp.json()
        # 1) 먼저 "response" 아래에 있을 수도, 아닐 수도 있으니 안전하게 추출
        if "response" in resp_json:
            body = resp_json["response"].get("body", {})
        else:
            body = resp_json.get("body", {})

        # 2) items가 dict일 수도, list일 수도 있으니 일관되게 리스트로 변환
        raw_items = body.get("items", [])
        if isinstance(raw_items, dict) and "item" in raw_items:
            data_items = raw_items["item"]
            if isinstance(data_items, dict):
                data_items = [data_items]
        elif isinstance(raw_items, list):
            data_items = raw_items
        else:
            data_items = []

        if not data_items:
            logger.warning("공공API에 후보 없음: %s", name)
            continue

        # 후보 이름 리스트
        candidate_names = [it["itemName"] for it in data_items]
        # 가장 비슷한 하나만 가져오기, 유사도 컷오프 0.6
        match = difflib.get_close_matches(name, candidate_names, n=1, cutoff=0.6)
        if match:
            details = next(it for it in data_items if it["itemName"] == match[0])
            logger.info("매칭된 제품명: %s → %s", name, match[0])
        else:
            # 컷오프 미달 시, 후보 첫 번째를 기본으로
            details = data_items[0]
            logger.info("첫번째 결과 사용: %s → %s", name, details.get("itemName"))

        # API 호출 실패 시 로깅
        if resp.status_code != 200:
            logger.info("e약은요 API 호출 실패: %s %s", resp.status_code, resp.text)
            continue

        # Medication 모델에 맞춰 저장
        med = Medication.objects.create(
            prescription=pres,
            name=name,
            dosage=dosage,
            pharmacy_name=item.get("pharmacy_name", ""),
            pharmacy_phone=item.get("pharmacy_phone", ""),
            hospital_name=item.get("hospital_name", ""),
            frequency_per_day=freq,
            manufacturer     = details.get("entpName", ""),
            efficacy         = details.get("efcyQesitm", ""),
            usage            = details.get("useMethodQesitm", ""),
            warning          = details.get("atpnWarnQesitm", ""),
            precautions      = details.get("atpnQesitm", ""),
            interaction      = details.get("intrcQesitm", ""),
            side_effects     = details.get("seQesitm", ""),
            storage          = details.get("depositMethodQesitm", ""),
            image_url        = details.get("itemImage", ""),
        )
    
    # 5) 품목분류 API 호출
    for item in meds_data:
        name   = item.get("name")
        try:
            med = Prescription.objects.get(id=prescription_id) \
                    .medications \
                    .get(name=name)
        except Medication.DoesNotExist:
            logger.warning("생성된 med 없음: %s", name)
            continue

        resp2 = requests.get(
            "http://apis.data.go.kr/1471000/DrugPrdlstVldPrdInfoService01/getDrugPrdlstVldPrdInfoService01",
            params={
                "serviceKey": decoded_key,
                "ITEM_NAME": name,
                "type": "json",
                "numOfRows": 1,
                "pageNo": 1,
            }
        )
        if resp2.status_code == 200:
            try:
                data2 = resp2.json()
            except ValueError:
                logger.warning("품목분류 API JSON 파싱 실패: %r", resp2.text)
                return

            # response 구조는 e약은요와 비슷하게 껍데기 안에 body → items
            body2 = data2.get("response", {}).get("body", {}) or data2.get("body", {})
            raw_items2 = body2.get("items", [])
            # dict 형태일 수도 있으니 리스트로 고정
            if isinstance(raw_items2, dict) and raw_items2.get("item"):
                items2 = raw_items2["item"]
                if isinstance(items2, dict):
                    items2 = [items2]
            elif isinstance(raw_items2, list):
                items2 = raw_items2
            else:
                items2 = []

            if items2:
                class_str = items2[0].get("CLASS_NO_NAME", "")
                categories = [c.strip() for c in class_str.split(",") if c.strip()]
                # ④ 인스턴스에 저장
                med.categories = categories
                med.save(update_fields=["categories"])
                logger.info("품목분류 저장: %s → %r", name, categories)
        else:
            logger.warning("품목분류 API 에러: %s %s", resp2.status_code, resp2.text)