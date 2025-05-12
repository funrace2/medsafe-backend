# prescriptions/urls.py

from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicationViewSet

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
# /api/prescriptions/medications/  → MedicationViewSet
router.register(r'medications', MedicationViewSet, basename='medication')
urlpatterns = router.urls
