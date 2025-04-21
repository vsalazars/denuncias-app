# config/urls.py o denuncias/urls.py (según tu estructura)
from django.urls import path
from denuncias.views import CustomTokenObtainPairView
from .views import actualizar_seguimiento


urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/seguimiento/', actualizar_seguimiento, name='actualizar_seguimiento'),
]
