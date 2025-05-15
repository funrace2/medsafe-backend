# prescriptions/urls.py

from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicationViewSet, CalendarMemoViewSet
from django.urls import path

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
# /api/prescriptions/medications/  → MedicationViewSet
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'memos', CalendarMemoViewSet, basename='calendar-memo')
urlpatterns = router.urls