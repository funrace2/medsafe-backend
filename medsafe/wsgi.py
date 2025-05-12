# medsafe/wsgi.py

"""
WSGI config for medsafe project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
# Cloud Run에서만 /secrets/vision.json 이 존재하므로, 있을 때만 설정
if os.path.exists("/secrets/vision.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/secrets/vision.json"

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medsafe.settings')

application = get_wsgi_application()
