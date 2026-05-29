# Guía de Prueba - Autenticación Biométrica WebAuthn

## Requisitos Previos

1. **Sistema Operativo:** Linux, macOS o Windows con WSL
2. **Navegador:** Chrome/Edge 67+, Firefox 60+, o Safari 13+
3. **HTTPS:** WebAuthn requiere HTTPS (excepto en localhost)
4. **Autenticador:** Dispositivo con soporte biométrico
   - Windows: Windows Hello (Windows 10/11)
   - macOS: Touch ID o Face ID
   - iOS: Face ID o Touch ID
   - Android: Huella dactilar o reconocimiento facial
   - USB Security Key: FIDO2

## Pasos para Probar Localmente

### 1. Iniciar el Servidor

```bash
cd /home/cesar/mis_proyectos/DentalPro
source .venv/bin/activate
python manage.py runserver
```

El servidor estará disponible en:
- HTTP: http://localhost:8000
- HTTPS (si está configurado): https://localhost:8443

**Nota:** WebAuthn no funciona en HTTP excepto en localhost.

### 2. Acceder al Login

Navega a: `http://localhost:8000/accounts/login/`

### 3. Prueba 1: Registro Biométrico

#### Pasos:
1. Ingresa tu nombre de usuario en el campo
2. Haz clic en "Registrar Biometría"
3. Se abrirá un diálogo del navegador
4. Selecciona tu dispositivo biométrico (Windows Hello, Touch ID, etc.)
5. Sigue las instrucciones del navegador
6. Se mostrará un mensaje de éxito

#### Validación:
```bash
# Verifica que se creó una credencial
python manage.py shell
>>> from core.models import WebAuthnCredential
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='tu_usuario')
>>> user.webauthn_credentials.all()
<QuerySet [<WebAuthnCredential: ...>]>
```

### 4. Prueba 2: Autenticación Biométrica

#### Pasos:
1. Cierra la sesión (si la hay)
2. En el login, ingresa tu nombre de usuario
3. Haz clic en "Entrar con Biometría"
4. Se abrirá un diálogo del navegador
5. Proporciona tus datos biométricos
6. Serás redirigido a `/pacientes/`

#### Validación:
```bash
# Verifica que el sign_count se incrementó
python manage.py shell
>>> from core.models import WebAuthnCredential
>>> cred = WebAuthnCredential.objects.first()
>>> print(f"Sign count: {cred.sign_count}")
>>> print(f"Last used: {cred.last_used_at}")
```

### 5. Prueba 3: Múltiples Credenciales

1. Registra un segundo dispositivo
2. Verifica que puedes autenticarte con cualquiera

```bash
python manage.py shell
>>> user = User.objects.get(username='tu_usuario')
>>> creds = user.webauthn_credentials.filter(is_active=True)
>>> print(f"Total credenciales activas: {creds.count()}")
```

## Pruebas Manuales Avanzadas

### Prueba: Desafíos Expirados

```bash
python manage.py shell
>>> from core.models import WebAuthnChallenge
>>> from django.utils import timezone
>>> from datetime import timedelta

# Ver desafíos activos
>>> active = WebAuthnChallenge.objects.filter(
...     expires_at__gt=timezone.now()
... )
>>> print(f"Desafíos activos: {active.count()}")

# Simular expiración
>>> old = WebAuthnChallenge.objects.create(
...     challenge='test',
...     challenge_type='register',
...     expires_at=timezone.now() - timedelta(minutes=1)
... )
>>> print(f"Desafío creado: {old.is_used}")

# Intentar usar desafío expirado
>>> expired = WebAuthnChallenge.objects.filter(
...     expires_at__lt=timezone.now()
... )
>>> print(f"Desafíos expirados: {expired.count()}")
```

### Prueba: Detección de Clonación

Para simular (NO HACER EN PRODUCCIÓN):

```bash
python manage.py shell
>>> from core.models import WebAuthnCredential

# Bajar el sign_count (simular clonación)
>>> cred = WebAuthnCredential.objects.first()
>>> original_count = cred.sign_count
>>> cred.sign_count = cred.sign_count - 1
>>> cred.save()

# Intentar autenticar - debería fallar
# Después, restaurar el valor correcto
>>> cred.sign_count = original_count
>>> cred.save()
```

### Prueba: Administración en Django Admin

1. Accede a `http://localhost:8000/admin/`
2. Ve a "Core → Credenciales WebAuthn"
3. Observa:
   - Lista de credenciales registradas
   - Información del dispositivo
   - Sign count y timestamps
   - Botones para marcar como inactiva

## Pruebas de Error

### Error: "El usuario no existe"
- Asegúrate de que el usuario existe en Django
- Prueba crear un usuario primero:

```bash
python manage.py createsuperuser
```

### Error: "Desafío inválido o expirado"
- Espera más de 10 minutos entre intentos
- Recarga la página para obtener un nuevo desafío
- Revisa los logs del servidor

### Error: "Credencial no encontrada"
- Asegúrate de haber registrado la credencial primero
- Intenta registrar nuevamente

### Error: "WebAuthn no está soportado"
- Tu navegador no soporta WebAuthn
- Actualiza a una versión más reciente
- Prueba con otro navegador

## Depuración en el Navegador

### Consola del Navegador

1. Abre las DevTools (F12)
2. Ve a la pestaña "Console"
3. Observa los logs de `webAuthnManager`:

```javascript
// Verificar soporte
console.log(webAuthnManager.isSupported())

// Ver información del dispositivo
console.log(webAuthnManager.getDeviceInfo())
```

### Almacenamiento Local

Abre DevTools → Storage → Local Storage:
- Los datos se transmiten por HTTPS/WebSocket, no se guardan localmente

## Monitoreo en Tiempo Real

### Logs del Servidor

```bash
# En otra terminal
tail -f /home/cesar/mis_proyectos/DentalPro/django.log
```

### Acceso a Base de Datos

```bash
python manage.py shell
>>> from core.models import WebAuthnCredential, WebAuthnChallenge
>>> from django.db.models import Q
>>> from django.utils import timezone

# Ver actividad reciente
>>> recent = WebAuthnChallenge.objects.filter(
...     created_at__gte=timezone.now() - timedelta(hours=1)
... ).order_by('-created_at')
>>> for challenge in recent:
...     print(f"{challenge.user} - {challenge.challenge_type} - {challenge.is_used}")
```

## Prueba de Carga (Opcional)

```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils

# Probar 100 solicitudes de login
ab -n 100 -c 10 http://localhost:8000/accounts/login/

# Probar WebAuthn register start (POST)
ab -n 50 -c 5 -p /tmp/data.json http://localhost:8000/core/api/webauthn/register/start/
```

## Limpieza de Datos de Prueba

```bash
python manage.py shell
>>> from core.models import WebAuthnCredential, WebAuthnChallenge
>>> from django.utils import timezone
>>> from datetime import timedelta

# Eliminar desafíos expirados
>>> WebAuthnChallenge.objects.filter(
...     expires_at__lt=timezone.now()
... ).delete()

# Eliminar credenciales inactivas de un usuario
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='test_user')
>>> user.webauthn_credentials.filter(is_active=False).delete()

# Limpiar TODO (CUIDADO)
>>> WebAuthnChallenge.objects.all().delete()
>>> WebAuthnCredential.objects.all().delete()
```

## Checklist de Validación

- [ ] Servidor Django inicia sin errores
- [ ] Login HTML carga correctamente
- [ ] Botones de biometría son visibles
- [ ] Registro biométrico funciona
- [ ] Autenticación biométrica funciona
- [ ] Múltiples credenciales funcionan
- [ ] Sign count se incrementa
- [ ] Desafíos se expiran correctamente
- [ ] Django Admin muestra credenciales
- [ ] Consola del navegador no tiene errores

## Soporte

Para reportar problemas:
1. Revisa los logs del servidor
2. Abre DevTools en el navegador
3. Copia los mensajes de error
4. Verifica la compatibilidad del navegador
5. Intenta en otro navegador
