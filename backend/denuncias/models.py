from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

ESTADOS_CHOICES = [
    ('AGS', 'Aguascalientes'),
    ('BC', 'Baja California'),
    ('BCS', 'Baja California Sur'),
    ('CAMP', 'Campeche'),
    ('CDMX', 'Ciudad de México'),
    ('CHIS', 'Chiapas'),
    ('CHIH', 'Chihuahua'),
    ('COAH', 'Coahuila'),
    ('COL', 'Colima'),
    ('DGO', 'Durango'),
    ('GTO', 'Guanajuato'),
    ('GRO', 'Guerrero'),
    ('HGO', 'Hidalgo'),
    ('JAL', 'Jalisco'),
    ('MEX', 'Estado de México'),
    ('MICH', 'Michoacán'),
    ('MOR', 'Morelos'),
    ('NAY', 'Nayarit'),
    ('NL', 'Nuevo León'),
    ('OAX', 'Oaxaca'),
    ('PUE', 'Puebla'),
    ('QRO', 'Querétaro'),
    ('QROO', 'Quintana Roo'),
    ('SLP', 'San Luis Potosí'),
    ('SIN', 'Sinaloa'),
    ('SON', 'Sonora'),
    ('TAB', 'Tabasco'),
    ('TAMPS', 'Tamaulipas'),
    ('TLAX', 'Tlaxcala'),
    ('VER', 'Veracruz'),
    ('YUC', 'Yucatán'),
    ('ZAC', 'Zacatecas'),
]


class CustomUserManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    rol = models.CharField(max_length=30)
    correo_enviado = models.BooleanField(default=False)  # 👈 Nuevo campo
    estado = models.CharField(max_length=50, choices=ESTADOS_CHOICES, blank=True, null=True)



    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.correo


class SeguimientoDenuncia(models.Model):
    ESTADO_SEGUIMIENTO_CHOICES = [
        ('EN_ANALISIS', 'En análisis por OIC'),
        ('TURNADA_AUTORIDAD', 'Turnada a Autoridad Investigadora (falta grave)'),
        ('TURNADA_FISCALIA', 'Turnada a Fiscalía Anticorrupción (corrupción)'),
        ('RECHAZADA', 'Rechazada por falta de elementos'),
        ('CONCLUIDA', 'Concluida con resolución del OIC (no grave)'),
    ]

    folio = models.CharField(max_length=100)
    estado = models.CharField(max_length=40, choices=ESTADO_SEGUIMIENTO_CHOICES, default='EN_ANALISIS')
    fecha_turno = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.folio} - {self.get_estado_display()}"

