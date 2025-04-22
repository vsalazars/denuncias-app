from django.contrib import admin
from .models import CustomUser, SeguimientoDenuncia, Dependencia
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('correo', 'first_name', 'last_name', 'rol', 'estado', 'is_staff')
    list_filter = ('rol', 'estado', 'is_staff')
    ordering = ('correo',)
    search_fields = ('correo', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'rol', 'estado', 'dependencia')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'first_name', 'last_name', 'password1', 'password2', 'rol', 'estado', 'dependencia', 'is_staff', 'is_superuser'),
        }),
    )


@admin.register(SeguimientoDenuncia)
class SeguimientoDenunciaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'estado', 'fecha_turno', 'comentario', 'dependencia')  # 👈 Se agregó dependencia
    list_filter = ('estado', 'dependencia')  # 👈 Se agregó filtro por dependencia
    search_fields = ('folio', 'comentario')
    ordering = ('-fecha_turno',)


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_rol', 'estado')  # 👈 ya incluye estado
    list_filter = ('tipo_rol', 'estado')
    search_fields = ('nombre',)
