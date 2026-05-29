# Implementación de Autenticación Biométrica WebAuthn/FIDO2

## Descripción General

Se ha implementado un sistema completo de autenticación biométrica FIDO2/WebAuthn para DentalPro, permitiendo a los usuarios registrarse y autenticarse usando sus datos biométricos (huella dactilar, reconocimiento facial, etc.) sin necesidad de contraseña.

## Componentes Implementados

### 1. **Modelos de Base de Datos** (`core/models.py`)

#### `WebAuthnCredential`
Almacena las credenciales biométricas registradas por cada usuario.

**Campos principales:**
- `user`: Relación con el usuario
- `credential_id`: ID único de la credencial
- `public_key`: Clave pública en formato CBOR/Base64
- `sign_count`: Contador de firmas (detecta clonación)
- `name`: Nombre descriptivo (ej: "Windows Hello", "Touch ID")
- `transports`: Transportes disponibles (USB, NFC, BLE, etc.)
- `aaguid`: Identificador del modelo de autenticador
- `last_used_at`: Última fecha de uso
- `is_active`: Estado de la credencial

#### `WebAuthnChallenge`
Almacena desafíos temporales durante registro y autenticación.

**Campos principales:**
- `user`: Usuario asociado (puede ser nulo para registro)
- `challenge`: Desafío único
- `challenge_type`: "register" o "authenticate"
- `expires_at`: Fecha de expiración (5-10 minutos)
- `is_used`: Marca si ya fue consumido

### 2. **Vistas de API** (`core/views.py`)

#### `WebAuthnRegisterStartView`
- **URL:** `POST /core/api/webauthn/register/start/`
- **Función:** Genera opciones de registro y un desafío
- **Request:** `{ "username": "usuario" }`
- **Response:** `{ "options": {...}, "success": true }`

#### `WebAuthnRegisterCompleteView`
- **URL:** `POST /core/api/webauthn/register/complete/`
- **Función:** Verifica la credencial registrada y la guarda
- **Request:** `{ "username": "usuario", "credential_name": "Mi dispositivo", "credential": {...} }`
- **Response:** `{ "success": true, "message": "..." }`

#### `WebAuthnAuthenticateStartView`
- **URL:** `POST /core/api/webauthn/authenticate/start/`
- **Función:** Genera opciones de autenticación y un desafío
- **Request:** `{ "username": "usuario" }`
- **Response:** `{ "options": {...}, "success": true }`

#### `WebAuthnAuthenticateCompleteView`
- **URL:** `POST /core/api/webauthn/authenticate/complete/`
- **Función:** Verifica la autenticación e inicia sesión
- **Request:** `{ "username": "usuario", "credential_id": "...", "credential": {...} }`
- **Response:** `{ "success": true, "message": "...", "redirect": "/pacientes/" }`

### 3. **Frontend JavaScript** (`core/static/js/webauthn.js`)

Clase `WebAuthnManager` que maneja:

- **`startRegistration(username)`**: Inicia el flujo de registro biométrico
- **`startAuthentication(username)`**: Inicia el flujo de autenticación biométrica
- **`prepareRegistrationOptions(options)`**: Convierte opciones para WebAuthn API
- **`prepareAuthenticationOptions(options)`**: Convierte opciones para WebAuthn API
- **`arrayBufferToBase64(buffer)`**: Convierte buffers para transmisión
- **`base64ToUint8Array(base64)`**: Convierte respuestas del servidor

### 4. **Template de Login** (`core/templates/core/login.html`)

Se agregaron:
- Botón "Entrar con Biometría"
- Botón "Registrar Biometría"
- Manejadores de alertas y errores
- Validación de entrada
- Detección automática de compatibilidad WebAuthn

### 5. **URLs** (`core/urls.py`)

```python
path('api/webauthn/register/start/', WebAuthnRegisterStartView.as_view(), name='webauthn_register_start'),
path('api/webauthn/register/complete/', WebAuthnRegisterCompleteView.as_view(), name='webauthn_register_complete'),
path('api/webauthn/authenticate/start/', WebAuthnAuthenticateStartView.as_view(), name='webauthn_authenticate_start'),
path('api/webauthn/authenticate/complete/', WebAuthnAuthenticateCompleteView.as_view(), name='webauthn_authenticate_complete'),
```

## Flujo de Registro

1. Usuario ingresa su nombre de usuario y hace clic en "Registrar Biometría"
2. Frontend solicita opciones de registro al backend
3. Backend genera un desafío y lo guarda
4. Frontend llama a `navigator.credentials.create()` con las opciones
5. Navegador solicita datos biométricos al usuario
6. Usuario proporciona su datos biométricos (huella, rostro, etc.)
7. Navegador crea una credencial y la devuelve al frontend
8. Frontend envía la credencial al backend
9. Backend verifica la credencial y la guarda en la BD

## Flujo de Autenticación

1. Usuario ingresa su nombre de usuario y hace clic en "Entrar con Biometría"
2. Frontend solicita opciones de autenticación al backend
3. Backend genera un desafío y lo guarda
4. Frontend llama a `navigator.credentials.get()` con las opciones
5. Navegador solicita datos biométricos al usuario
6. Usuario proporciona sus datos biométricos
7. Navegador crea una asserción y la devuelve al frontend
8. Frontend envía la asserción al backend
9. Backend verifica la asserción contra la credencial guardada
10. Si es válida, inicia sesión del usuario

## Seguridad

### Medidas Implementadas

1. **Desafíos únicos**: Cada registro/autenticación genera un desafío único
2. **Expiración de desafíos**: Los desafíos expiran en 5-10 minutos
3. **Verificación de origen**: Se verifica que el origen coincida
4. **Verificación de RP ID**: Se valida el ID de la Relying Party
5. **Contador de firmas**: Se detecta clonación verificando `sign_count`
6. **CSRF protection**: Las vistas usan `@csrf_exempt` pero solo para POST JSON
7. **User verification**: Se solicita verificación del usuario cuando es posible

### Flujo Anti-Clonación

Si un dispositivo es clonado, el contador de firmas original será mayor que el del clon, lo que causará el rechazo automático de la autenticación.

```python
if verification.new_sign_count <= credential.sign_count:
    return JsonResponse(
        {'error': 'Posible clonación de autenticador detectada'},
        status=400
    )
```

## Compatibilidad del Navegador

WebAuthn está soportado en:
- Chrome/Edge 67+
- Firefox 60+
- Safari 13+
- Android Chrome
- iOS Safari (parcial)

El frontend detecta automáticamente la falta de soporte y oculta los botones biométricos.

## Datos Técnicos

### Credenciales Almacenadas

Las credenciales se almacenan en formato CBOR (Concise Binary Object Representation) codificado en Base64:

```
public_key = base64(cbor2.dumps(credential_public_key))
```

### Soportar Múltiples Credenciales

Un usuario puede registrar varias credenciales (ej: Windows Hello en la oficina, Touch ID en el móvil):

```python
credentials = WebAuthnCredential.objects.filter(
    user=user,
    is_active=True
)
```

### Información del Dispositivo

El nombre de la credencial se detecta automáticamente según el navegador:
- Windows: "Windows Hello"
- macOS: "Touch ID / Face ID"
- iOS: "Face ID / Touch ID"
- Android: "Android Biometric"

## Administración en Django Admin

Se pueden administrar credenciales y desafíos desde Django Admin:

```python
# core/admin.py
from django.contrib import admin
from .models import WebAuthnCredential, WebAuthnChallenge

admin.site.register(WebAuthnCredential)
admin.site.register(WebAuthnChallenge)
```

## Mantenimiento

### Limpieza de Desafíos Expirados

Ejecutar periódicamente con Celery o cron:

```python
from django.utils import timezone
from core.models import WebAuthnChallenge

# Eliminar desafíos expirados
WebAuthnChallenge.objects.filter(
    expires_at__lt=timezone.now()
).delete()
```

### Desactivar Credencial

```python
credential = WebAuthnCredential.objects.get(pk=credential_id)
credential.is_active = False
credential.save()
```

## Troubleshooting

### "Error al obtener opciones de registro"
- Verificar que el usuario existe
- Revisar logs del servidor

### "Error al verificar el registro"
- El navegador puede haber cancelado el registro
- Probar con otro autenticador
- Revisar la consola del navegador para más detalles

### "Credencial no encontrada"
- La credencial puede haber sido eliminada
- El ID de credencial puede ser incorrecto
- Intentar registrar nuevamente

### WebAuthn no aparece soportado
- Actualizar el navegador
- Usar HTTPS (requerido para WebAuthn en navegadores modernos)
- Verificar que el navegador soporta WebAuthn

## Referencias

- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [py_webauthn Documentation](https://github.com/duo-labs/py_webauthn)
- [MDN - Web Authentication API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)
- [FIDO2 Specifications](https://fidoalliance.org/fido2/)
