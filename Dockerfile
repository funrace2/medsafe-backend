# Dockerfile

# 1. 베이스 이미지
FROM python:3.12-slim

# 2. 비표준 출력 활성화 (로깅 시 바로 출력)
ENV PYTHONUNBUFFERED=1
# ENV PORT=8080

# 3. 작업 디렉터리 설정
WORKDIR /app

# 4. 시스템 종속성 (DB 드라이버 등) 설치
# RUN apt-get update \
# && apt-get install -y --no-install-recommends \
#    build-essential libpq-dev \
# && rm -rf /var/lib/apt/lists/*

# 5. requirements 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 복사
COPY . .

# 7. (선택) static 파일 모아서 배포용으로 준비
#    만약 Django에서 collectstatic 사용 중이라면 활성화
# RUN python manage.py collectstatic --noinput


# 8. 컨테이너가 수신할 포트
EXPOSE 8080

# Gunicorn 을 이용해 WSGI 앱 실행
# --bind 0.0.0.0:$PORT 로 외부(Cloud Run) 트래픽 수신
ENTRYPOINT gunicorn medsafe.wsgi:application --bind 0.0.0.0:$PORT