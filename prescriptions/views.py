# prescriptions/views.py

from rest_framework import viewsets
from .models import Prescription, Medication
from .serializers import PrescriptionSerializer, MedicationSerializer
from .tasks import process_prescription
from core.utils import upload_image_to_gcs
import logging
logger = logging.getLogger(__name__)
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def perform_create(self, serializer):
        # user는 Serializer가 자동으로 채워주니, 바로 save()
        logger.warning("🔥 perform_create 실행됨")
        logger.warning("🔐 request.user: %s / 인증됨: %s", self.request.user, self.request.user.is_authenticated)
        image_file = self.request.FILES.get("image")
        image_url = upload_image_to_gcs(image_file) if image_file else None
        prescription = serializer.save(user=self.request.user, image_url=image_url)
        logger.warning("✅ 처방 생성됨: id=%s", prescription.id)
        try:
            process_prescription.delay(prescription.id)
        except Exception:
            logger.exception("❌ Celery task 호출 실패:")
        logger.warning("✅ Celery 호출됨: %s", prescription.id)
class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    