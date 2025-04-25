# prescriptions/views.py

from rest_framework import viewsets
from .models import Prescription
from .serializers import PrescriptionSerializer
from .tasks import process_prescription

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def perform_create(self, serializer):
        # 요청한 사용자 정보까지 함께 저장하려면:
        serializer.save(user=self.request.user)
        pres = serializer.save(user=self.request.user)
        # 비동기로 OCR + API 처리를 위임
        process_prescription.delay(pres.id)
