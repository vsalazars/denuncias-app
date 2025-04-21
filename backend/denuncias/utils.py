from django.core.mail import send_mail

def enviar_datos_usuario(correo, password, rol):
    asunto = '📥 Tu cuenta en la Plataforma de Denuncias ha sido creada'
    mensaje = (
        f"Hola,\n\n"
        f"Se ha creado una cuenta para ti en la Plataforma de Denuncias.\n"
        f"Correo: {correo}\n"
        f"Contraseña: {password}\n"
        f"Rol asignado: {rol}\n\n"
        f"Puedes ingresar en: http://localhost:5173/\n\n"
        f"Por favor, cambia tu contraseña al ingresar.\n\n"
        f"Atentamente,\nSistema de Denuncias"
    )
    send_mail(asunto, mensaje, 'vsalazar@sesna.gob.mx', [correo])
