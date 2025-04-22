from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, SeguimientoDenuncia, Dependencia


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'correo'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token  # no hace falta extender aquí

    def validate(self, attrs):
        correo = attrs.get('correo')
        password = attrs.get('password')

        user = authenticate(request=self.context.get("request"), correo=correo, password=password)

        if not user:
            raise serializers.ValidationError("Correo o contraseña incorrectos")

        refresh = self.get_token(user)
        access = refresh.access_token

        # ✅ Estos campos irán en el token
        access['rol'] = user.rol
        access['correo'] = user.correo
        access['first_name'] = user.first_name or ''
        access['last_name'] = user.last_name or ''
        access['estado'] = user.estado or ''
        access['dependencia_id'] = user.dependencia.id if user.dependencia else None

        return {
            'refresh': str(refresh),
            'access': str(access),
        }

class DependenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependencia
        fields = ['id', 'nombre', 'tipo_rol']


class CustomUserSerializer(serializers.ModelSerializer):
    dependencia = DependenciaSerializer(read_only=True)
    dependencia_id = serializers.PrimaryKeyRelatedField(
        queryset=Dependencia.objects.all(),
        source='dependencia',
        write_only=True,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'correo', 'first_name', 'last_name', 'rol', 'estado',
            'correo_enviado', 'dependencia', 'dependencia_id'
        ]

    def validate(self, data):
        if data.get('rol') != 'ADMIN' and not data.get('estado'):
            raise serializers.ValidationError("El estado es obligatorio para todos los roles excepto ADMIN.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            from django.utils.crypto import get_random_string
            user.set_password(get_random_string(12))
        user.save()
        return user


class SeguimientoSerializer(serializers.ModelSerializer):
    dependencia = DependenciaSerializer(read_only=True)
    dependencia_id = serializers.PrimaryKeyRelatedField(
        queryset=Dependencia.objects.all(),
        source='dependencia',
        write_only=True,
        required=False
    )

    class Meta:
        model = SeguimientoDenuncia
        fields = ['folio', 'estado', 'comentario', 'fecha_turno', 'dependencia', 'dependencia_id']
        read_only_fields = ['fecha_turno']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.fecha_turno:
            data['fecha_turno'] = instance.fecha_turno.isoformat()
        return data

