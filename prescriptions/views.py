# prescriptions/views.py

from rest_framework import viewsets
from .models import Prescription
from .serializers import PrescriptionSerializer
from .tasks import process_prescription

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def perform_create(self, serializer):
        # user는 Serializer가 자동으로 채워주니, 바로 save()
        prescription = serializer.save()
        process_prescription.delay(prescription.id)