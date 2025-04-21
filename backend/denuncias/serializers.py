from rest_framework import serializers
from django.contrib.auth import authenticate  # ✅ necesario para usar authenticate
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import SeguimientoDenuncia


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'correo'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ✅ AÑADE datos al token aquí
        token['rol'] = user.rol
        token['correo'] = user.correo
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['estado'] = user.estado  # ✅ este campo es clave ahora


        return token

    def validate(self, attrs):
        correo = attrs.get('correo')
        password = attrs.get('password')

        user = authenticate(request=self.context.get("request"), correo=correo, password=password)

        if not user:
            raise serializers.ValidationError("Correo o contraseña incorrectos")

        refresh = self.get_token(user)
        access = refresh.access_token

        return {
            'refresh': str(refresh),
            'access': str(access),
        }


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'correo', 'first_name', 'last_name', 'rol', 'estado', 'correo_enviado']
 
    def validate(self, data):
        if data.get('rol') != 'ADMIN' and not data.get('estado'):
            raise serializers.ValidationError("El estado es obligatorio para todos los roles excepto ADMIN.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)  # ⚠️ puede venir None
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            from django.utils.crypto import get_random_string
            user.set_password(get_random_string(12))  # contraseña aleatoria segura
        user.save()
        return user


class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoDenuncia
        fields = ['folio', 'estado', 'comentario', 'fecha_turno']
        read_only_fields = ['fecha_turno']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.fecha_turno:
            data['fecha_turno'] = instance.fecha_turno.isoformat()
        return data
