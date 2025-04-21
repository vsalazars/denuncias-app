from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.db.models import Max  # ✅ NECESARIO para obtener fecha más reciente

import secrets
import string
import random

from .models import CustomUser, SeguimientoDenuncia
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer, SeguimientoSerializer
from .utils import enviar_datos_usuario
from datetime import date


# ✅ Vista para autenticación personalizada
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ✅ Vista para crear/modificar cualquier usuario (uso general)
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


# ✅ Vista para el admin (solo admins pueden usar esta)
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Generar una contraseña segura automáticamente
        password = ''.join(secrets.choice(string.ascii_letters + string.digits + '@#%&') for i in range(12))
        user = serializer.save()
        user.set_password(password)

        try:
            enviar_datos_usuario(user.correo, password, user.rol)
            user.correo_enviado = True
        except Exception as e:
            print("❌ Error al enviar el correo:", e)
            user.correo_enviado = False

        user.save()


# ✅ Crear un nuevo seguimiento (no reemplaza el anterior)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seguimiento_denuncia(request):
    print("💡 Datos recibidos:", request.data)

    serializer = SeguimientoSerializer(data=request.data)
    if serializer.is_valid():
        seguimiento = serializer.save()
        return Response(SeguimientoSerializer(seguimiento).data, status=status.HTTP_201_CREATED)
    else:
        print("❌ Errores del serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Obtener el último seguimiento por folio
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ultimos_seguimientos(request):
    """
    Devuelve el último seguimiento (por fecha) por cada folio.
    """
    try:
        # Obtenemos la fecha más reciente por folio
        ultimos = (
            SeguimientoDenuncia.objects.values('folio')
            .annotate(max_fecha=Max('fecha_turno'))
        )

        # Filtramos los objetos con la fecha más reciente para cada folio
        seguimientos = []
        for u in ultimos:
            seguimiento = SeguimientoDenuncia.objects.filter(
                folio=u['folio'],
                fecha_turno=u['max_fecha']
            ).first()
            if seguimiento:
                seguimientos.append(seguimiento)

        serializer = SeguimientoSerializer(seguimientos, many=True)
        return Response(serializer.data)

    except Exception as e:
        print("❌ Error en obtener_ultimos_seguimientos:", str(e))
        return Response({'error': 'Error interno del servidor'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_por_folio(request, folio):
    seguimientos = SeguimientoDenuncia.objects.filter(folio=folio).order_by('-fecha_turno')
    serializer = SeguimientoSerializer(seguimientos, many=True)
    return Response(serializer.data)
