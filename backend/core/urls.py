from django.urls import path, include
from rest_framework import routers
from .views import (
    CampaignViewSet, BeneficiaryViewSet, TaskViewSet, RegisterView, EmailTokenObtainPairView
)

router = routers.DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'beneficiaries', BeneficiaryViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='login'),
]
