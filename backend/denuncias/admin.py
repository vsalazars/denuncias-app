from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SeguimientoDenuncia


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('correo', 'first_name', 'last_name', 'rol', 'estado', 'is_staff')
    list_filter = ('rol', 'estado', 'is_staff')
    ordering = ('correo',)
    search_fields = ('correo', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'rol', 'estado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'first_name', 'last_name', 'password1', 'password2', 'rol', 'estado', 'is_staff', 'is_superuser'),
        }),
    )


# ✅ Registro del modelo SeguimientoDenuncia
@admin.register(SeguimientoDenuncia)
class SeguimientoDenunciaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'estado', 'fecha_turno', 'comentario')  # ← ahora muestra comentario
    list_filter = ('estado',)
    search_fields = ('folio', 'comentario')  # ← permite buscar por comentario
    ordering = ('-fecha_turno',)