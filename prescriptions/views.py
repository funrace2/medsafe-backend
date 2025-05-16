# prescriptions/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Prescription, Medication, CalendarMemo
from .serializers import PrescriptionSerializer, MedicationSerializer, CalendarMemoSerializer
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
        self.prescription = serializer.save(user=self.request.user, image_url=image_url)
        logger.warning("✅ 처방 생성됨: id=%s", self.prescription.id)
        try:
            process_prescription.delay(self.prescription.id)
        except Exception:
            logger.exception("❌ Celery task 호출 실패:")
        logger.warning("✅ Celery 호출됨: %s", self.prescription.id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data['image_url'] = getattr(self, 'prescription', None).image_url if hasattr(self, 'prescription') else None
        return response
    
class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    
class CalendarMemoViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarMemoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarMemo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        date = request.data.get('date')
        content = request.data.get('content')

        if not date:
            return Response({'error': 'date is required'}, status=status.HTTP_400_BAD_REQUEST)

        memo, created = CalendarMemo.objects.update_or_create(
            user=request.user,
            date=date,
            defaults={'content': content}
        )

        serializer = self.get_serializer(memo)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

