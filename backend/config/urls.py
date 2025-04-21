from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from denuncias.views import (
    UserViewSet,
    CustomTokenObtainPairView,
    seguimiento_denuncia,
    obtener_ultimos_seguimientos ,
    historial_por_folio   
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/', include(router.urls)),
    path('api/seguimiento/', seguimiento_denuncia, name='seguimiento_denuncia'),
    path('api/seguimientos/ultimos/', obtener_ultimos_seguimientos),
    path('api/seguimientos/folio/<str:folio>/', historial_por_folio),

]
