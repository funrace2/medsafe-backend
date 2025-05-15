# prescriptions/tasks.py

import json
import difflib
import re
import os
from urllib.parse import unquote
from celery import shared_task
from google.cloud import vision
from google.oauth2 import service_account
from google import genai
import requests
from .models import Prescription, Medication
from django.conf import settings
from rapidfuzz import process as rf_process, fuzz as rf_fuzz
import traceback
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import MedicationSerializer
import logging
logger = logging.getLogger(__name__)
# .env에서 불러온 원본 키
raw_key = settings.OPEN_API_KEY
# URL 디코딩
decoded_key = unquote(raw_key)

@shared_task
def process_prescription(prescription_id):
    try:
        logger.warning("✅ Task 시작: prescription_id=%s", prescription_id)
        # 1) Prescription 인스턴스
        pres = Prescription.objects.get(id=prescription_id)
        logger.warning("📦 Prescription 로드됨: %s", pres)

        # 1) Gemini API 키 설정 (환경변수 또는 .env에 GEN_API_KEY)
        genai.Client(api_key=settings.GEN_API_KEY)

        # 명시적으로 credentials 객체 로드
        credentials = service_account.Credentials.from_service_account_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        )
        # 2) OCR
        client = vision.ImageAnnotatorClient(credentials=credentials)
        logger.warning("🌐 이미지 URL: %s", pres.image_url)
        image = vision.Image()
        image.source.image_uri = pres.image_url
        response = client.text_detection(image=image)
        pres.ocr_text = response.full_text_annotation.text
        pres.save(update_fields=['ocr_text'])
        logger.warning("✅ OCR 완료: %s", pres.ocr_text[:100])

    except Exception as e:
        logger.exception("❌ Task 내부 예외 발생: %s\n%s", e, traceback.format_exc())

    # 3) Gemini에게 파싱 요청
    prompt = f"""
    아래 처방전 또는 약봉투 텍스트에서 약 이름(name), 1회 투여량(dosage), 1일 투여횟수(frequency), 약국 이름(pharmacy_name), 약국 전화번호(pharmacy_phone), 병원 이름(hospital_name)을
    JSON 리스트 형태로 추출해 주세요. 이때 약 이름은 약학정보원에서 제공하는 약품명과 일치해야 합니다.
    약 이름에 투여량, 투여횟수가 포함되면 안됩니다. 예를 들어 한올트리메부틴말레산염/1정이 아니라 한올트리메부틴말레산염만 포함되어야 합니다.
    약국 이름에는 "약국"이라는 단어가 포함되어야 합니다.
    **주의사항**:
    - "name"이 빠진 약품은 JSON에 포함하지 마세요.

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

    new_meds = []

    def normalize_name(raw_name):
        if not raw_name:
            return ""
        # 숫자+단위(정, 캡슐, mg, g, ml) 제거
        cleaned = re.sub(r'[\d\.]+\s*(mg|g|정|ml|캡슐)', '', raw_name, flags=re.IGNORECASE)
        # 남은 “정” 같은 단어 한 번 더 제거
        cleaned = re.sub(r'(정|캡슐)$', '', cleaned)
        return cleaned.strip()

    # 4) 공공약 API 호출 및 DB 저장
    for item in meds_data:
        name   = item.get("name")
        dosage = item.get("dosage")
        freq   = item.get("frequency", 0)
        base_name = normalize_name(item.get("name"))
        # e약은요 서비스 호출
        resp = requests.get(
            "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList",
            params={
                "serviceKey": decoded_key,  # URL 디코딩된 키
                "itemName": base_name,       # 처방전에서 추출한 약 이름
                "type": "json",
                "numOfRows": 50,
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
            # 공공 API 에 후보가 없더라도 최소한의 정보로 Medication 생성
            logger.warning("공공API에 후보 없음: %s — 기본 정보로 생성합니다.", name)
            med = Medication.objects.create(
                prescription=pres,
                name=name,
                dosage=dosage,
                pharmacy_name=item.get("pharmacy_name", ""),
                pharmacy_phone=item.get("pharmacy_phone", ""),
                hospital_name=item.get("hospital_name", ""),
                frequency_per_day=freq,
                # 공공 API 필드들은 비워두기
                manufacturer="",
                efficacy="",
                usage="",
                warning="",
                precautions="",
                interaction="",
                side_effects="",
                storage="",
                image_url="",
            )
            new_meds.append(med)
            # 아래 상세 매칭 로직을 건너뛰고 다음 약으로
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
        new_meds.append(med)
    
    # 5) 품목분류 API 호출
    for item in meds_data:
        name   = item.get("name")
        try:
            med = Prescription.objects.get(id=prescription_id) \
                    .medications \
                    .filter(name=name) \
                    .first()
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
                # 인스턴스에 저장
                med.categories = categories
                med.save(update_fields=["categories"])
                logger.info("품목분류 저장: %s → %r", name, categories)
        else:
            logger.warning("품목분류 API 에러: %s %s", resp2.status_code, resp2.text)

    # 6) 분류 키워드 기반 상호작용 감지 (유사도 기준)
    # 현재 처방전에 속하지 않는, 같은 유저의 다른 처방전 약들
    existing_meds = Medication.objects.filter(
        prescription__user=pres.user
    ).exclude(prescription=pres)
    warnings = []
    THRESHOLD = 60  # 유사도 컷오프 (0~100)

    for new in new_meds:
        for old in existing_meds:
            # 1) old.interaction 텍스트 vs new.categories 키워드
            for cat in new.categories:
                score = rf_fuzz.partial_ratio(cat, old.interaction or "")
                if score >= THRESHOLD:
                    warnings.append({
                        "new": new.name,
                        "old": old.name,
                        "keyword": cat,
                        "score": score,
                        "direction": "new→old"
                    })
                    break

            # 2) new.interaction 텍스트 vs old.categories 키워드
            for cat in old.categories:
                score = rf_fuzz.partial_ratio(cat, new.interaction or "")
                if score >= THRESHOLD:
                    warnings.append({
                        "new": new.name,
                        "old": old.name,
                        "keyword": cat,
                        "score": score,
                        "direction": "old→new"
                    })
                    break

    # 중복 제거
    unique = { (w["new"], w["old"], w["keyword"], w["direction"]) : w for w in warnings }
    med.interaction_warnings = list(unique.values())
    med.save(update_fields=["interaction_warnings"])

    profile = pres.user.profile
    THRESHOLD = 70

    # 7) 알러지 및 지병 충돌 검사
    for med in new_meds:
        text = med.precautions or ""

        # 1) 알러지 검사
        a_warns = []
        for term in profile.allergies:
            if rf_fuzz.partial_ratio(term, text) >= THRESHOLD:
                a_warns.append({"term":term})
        med.allergy_warnings = a_warns

        # 2) 지병 검사
        d_warns = []
        for term in profile.chronic_diseases:
            if rf_fuzz.partial_ratio(term, text) >= THRESHOLD:
                d_warns.append({"term":term})
        med.condition_warnings = d_warns

        # 변경된 두 필드만 저장
        med.save(update_fields=["allergy_warnings","condition_warnings"])

    # 8) WebSocket 알림 보내기
    channel_layer = get_channel_layer()
    meds_data = MedicationSerializer(new_meds, many=True).data

    async_to_sync(channel_layer.group_send)(
        f"user_{pres.user.id}",
        {
            "type": "prescription.done",
            "message": "약 정보가 생성되었습니다.",
            "prescription_id": pres.id,
            "medications": meds_data,
        }
    )

    logger.info("📡 WebSocket 알림 전송 완료: user_%s", pres.user.id)
