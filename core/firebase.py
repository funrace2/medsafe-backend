# core/firebase.py

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

# 이미 초기화된 앱이 없으면
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# def send_push(token: str, title: str, body: str, data: dict = None) -> str:
#     """
#     단일 디바이스(token)로 푸시 전송.
#     data는 key/value 형태로 custom data 페이로드를 보낼 때 사용합니다.
#     반환값: FCM 메시지 ID
#     """
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body,
#         ),
#         token=token,
#         data=data or {},
#     )
#     # send() 는 성공하면 message ID 문자열을 반환합니다.
#     return messaging.send(message)
