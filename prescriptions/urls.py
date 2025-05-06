# prescriptions/urls.py

from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicationViewSet

router = DefaultRouter()
# /api/prescriptions/medications/  → MedicationViewSet
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'', PrescriptionViewSet, basename='prescription')
urlpatterns = router.urls
