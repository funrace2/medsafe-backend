# 💊 MedSafe
[English README →](./README_en.md)

**MedSafe**는 청년층을 위한 **복약 정보 조회 및 복용 관리 서비스**를 지원하는 **이약저약** 애플리케이션의 **백엔드** 시스템입니다.  
이 프로젝트는 **Google Solution Challenge 2025**의 일환으로 개발되었으며, RESTful API를 통해 **의약품 정보 자동 조회**, **처방전 관리**, **복용 알림 기능**을 제공합니다.

---

## ✅ 프로젝트 개요

청년층의 복약 순응도는 낮은 건강 인식과 직관적인 관리 도구의 부재로 인해 낮은 편입니다.  
**MedSafe**는 사용자가 번거로움 없이 꾸준한 복약 습관을 유지할 수 있도록 돕는 **사용자 친화적 플랫폼**을 목표로 합니다.

---

## ⚙️ 주요 기능

- **OCR 및 AI 기반 의약품 인식**  
  Google Cloud Vision API로 처방전 이미지를 분석하고 Gemini(구글 LLM)을 이용해 모호한 약물 관련 질의에 대화형으로 응답합니다.

- **의약품 정보 자동 조회**  
  OCR로 인식된 약품명 또는 품목코드를 기반으로 공공데이터 API **e약은요**를 조회해 효능, 용법, 주의사항, 상호작용, 부작용 등 상세 정보를 자동으로 제공합니다.

- **처방전 업로드 및 관리**  
  사용자는 처방전 이미지를 업로드할 수 있으며 서버는 이를 **Google Cloud Storage**에 저장하고 기록 관리 기능을 제공합니다.

- **캘린더 기반 복용 기록 및 알림**  
  개인 캘린더를 통해 복용 내역을 기록하고 메모 및 알림을 추가할 수 있습니다.

- **대화형 약물 정보 챗봇**  
  사용자가 자연어로 약에 대해 질문하면 챗봇이 AI를 활용해 관련 정보를 제공합니다.

---

## 🛠️ 기술 스택

- **프레임워크**: Django (Django REST Framework)  
- **데이터베이스**: PostgreSQL  
- **AI 서비스**: Google Cloud Vision API, Gemini (LLM)  
- **배포 환경**: Google Cloud Run, Docker  
- **기타 구성요소**: Celery, Upstash Redis, Google Cloud Storage, Task Queue

---

## 📁 프로젝트 구조

```plaintext
medsafe-backend/
├── chat/                 # 챗봇 로직
├── core/                 # 공용 유틸리티 및 클라우드 스토리지 로직
├── prescriptions/        # 처방전 및 약물 관련 모델·뷰
├── calendar/             # 복용 일정 및 메모 관리
├── manage.py             # Django 실행 엔트리 포인트
├── requirements.txt      # Python 의존성 목록
├── Dockerfile, Procfile  # 배포 설정 파일
```

---

## 🚀 로컬 개발 환경 설정

```bash
git clone https://github.com/funrace2/medsafe-backend.git
cd medsafe-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔐 주요 API 예시

- `POST /api/prescriptions/`  
  처방전 이미지 및 데이터를 업로드 (인증 필요)

- `GET /api/chat/medications/?query=headache`  
  챗봇을 통해 약물 정보를 질의

- `GET /api/calendar/memos/`  
  사용자 개인의 복용 메모 조회

---

## ☁️ 배포 환경

본 백엔드는 **Google Cloud Run** 위에서 구동되며 비동기 작업은 **Celery**와 **Upstash Redis**로 처리됩니다.

---

## 📣 참고 자료

- OCR: Google Cloud Vision API  
- 자연어 이해: Gemini LLM  
- 약품 정보: [DrbEasyDrugInfoService - Data.go.kr](https://www.data.go.kr/data/15075057/openapi.do)  
- 추가 식별 정보: [식별정보조회 API](https://www.data.go.kr/data/15057639/openapi.do#/API%20목록/getMdcinGrnIdntfcInfoList02)  

---

## 🙋 기여자 및 문의

- **Backend Developer**: 구현모 (Hyeonmo Koo)  
- **문의**: [GitHub Issues](https://github.com/funrace2/medsafe-backend/issues)
