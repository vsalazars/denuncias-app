from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'correo'

    def validate(self, attrs):
        correo = attrs.get('correo')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), correo=correo, password=password)

        if not user:
            raise serializers.ValidationError('Correo o contraseña incorrectos')

        refresh = self.get_token(user)
        access = refresh.access_token

        # ✅ Asegúrate de que estos campos estén en el modelo y contengan valor
        access['rol'] = user.rol
        access['correo'] = user.correo
        access['first_name'] = user.first_name or ''
        access['last_name'] = user.last_name or ''
        # 👇 Estas dos líneas nuevas
        access['estado'] = user.estado or ''
        access['dependencia_id'] = user.dependencia.id if user.dependencia else None  # ✅ este es el que falta

        return {
            'refresh': str(refresh),
            'access': str(access),
        }
