--- AUDITORIA_INTEGRAL.md (原始)


+++ AUDITORIA_INTEGRAL.md (修改后)
# 📋 AUDITORÍA TÉCNICA INTEGRAL - DentalPro

## Estado Actual del Proyecto

**Fecha de Auditoría:** Mayo 29, 2024
**Versión:** v1.0-alpha
**Estado:** ✅ Sistema funcional validado

---

## 📚 Documentación Revisada

1. **README.md** - Documentación principal del proyecto
2. **ux_audit_report.md** - Auditoría UX y frontend completada
3. **VALIDATION.md** - Instrucciones de validación
4. **IMPLEMENTATION_SUMMARY.md** - Resumen implementación WebAuthn
5. **WEBAUTHN_IMPLEMENTATION.md** - Guía técnica WebAuthn
6. **TESTING_WEBAUTHN.md** - Guía de pruebas WebAuthn
7. **WEBAUTHN_CLI.md** - Comandos CLI WebAuthn
8. **QUICKSTART.md** - Inicio rápido WebAuthn

---

## 🔍 FASES DE AUDITORÍA

### FASE 0: Validación de Infraestructura ✅ COMPLETADO

**Comando ejecutado:**
```bash
python manage.py check --settings=config.settings.dev
# Resultado: System check identified no issues (0 silenced).
```

**Dependencias instaladas:**
- Django==4.2.13 ✓
- webauthn==2.2.0 ✓
- cbor2 ✓
- daphne ✓
- channels ✓
- redis ✓
- strawberry-graphql[django] ✓

---

### FASE 1: Auditoría de Modelos WebAuthn

**Archivos auditados:**
- `/workspace/core/models.py`

**Hallazgos:**
✅ Modelo `WebAuthnCredential` implementado correctamente
✅ Modelo `WebAuthnChallenge` implementado correctamente
✅ Campos adecuados para almacenamiento seguro
✅ Índices en credential_id y challenge
✅ unique_together configurado
✅ Timestamps automáticos
✅ Estado is_active para habilitar/deshabilitar

**Recomendaciones:**
1. Agregar método para obtener credenciales activas por usuario
2. Agregar método estático para limpiar desafíos expirados
3. Considerar agregar campo para último IP de uso

---

### FASE 2: Auditoría de Vistas API WebAuthn

**Archivos auditados:**
- `/workspace/core/views.py`

**Hallazgos:**
✅ 4 vistas API REST implementadas
✅ Registro: start/complete
✅ Autenticación: start/complete
✅ Verificación de desafíos con expiración
✅ Detección de clonación via sign_count
✅ Manejo de errores con JsonResponse
✅ CSRF exempt solo para endpoints JSON

**Recomendaciones:**
1. Agregar logging de intentos fallidos
2. Agregar rate limiting para prevenir fuerza bruta
3. Considerar agregar headers de seguridad adicionales
4. Normalizar manejo de excepciones

---

### FASE 3: Auditoría de Frontend WebAuthn

**Archivos por auditar:**
- `/workspace/core/static/js/webauthn.js`
- `/workspace/core/templates/core/login.html`

**Pendientes de verificación:**
- [ ] Verificar existencia de webauthn.js
- [ ] Verificar integración en login.html
- [ ] Verificar detección de soporte del navegador
- [ ] Verificar manejo de errores en frontend

---

### FASE 4: Auditoría de Administración Django

**Archivos por auditar:**
- `/workspace/core/admin.py`

**Pendientes de verificación:**
- [ ] Verificar registro de modelos en admin
- [ ] Verificar actions personalizadas
- [ ] Verificar filtros y búsquedas

---

### FASE 5: Auditoría de Comandos CLI

**Archivos por auditar:**
- `/workspace/core/management/commands/webauthn.py`

**Pendientes de verificación:**
- [ ] Verificar subcomandos implementados
- [ ] Probar comando `list`
- [ ] Probar comando `stats`
- [ ] Probar comando `clean-challenges`
- [ ] Probar comando `disable`
- [ ] Probar comando `user-info`

---

### FASE 6: Auditoría de Migraciones

**Archivos por verificar:**
- `/workspace/core/migrations/`

**Pendientes:**
- [ ] Verificar existencia de migraciones
- [ ] Ejecutar migraciones pendientes
- [ ] Verificar consistencia de base de datos

---

### FASE 7: Auditoría de URLs

**Archivos por auditar:**
- `/workspace/core/urls.py`

**Pendientes:**
- [ ] Verificar rutas de API WebAuthn
- [ ] Verificar nombres de URL
- [ ] Verificar inclusión en urls principales

---

### FASE 8: Auditoría de Seguridad

**Aspectos a verificar:**
- [ ] HTTPS requerido en producción
- [ ] Validación de origen en WebAuthn
- [ ] Expiración de desafíos
- [ ] Protección CSRF
- [ ] Logging de eventos críticos
- [ ] Rate limiting en endpoints

---

### FASE 9: Auditoría de Rendimiento

**Aspectos a verificar:**
- [ ] Índices de base de datos
- [ ] Consultas N+1
- [ ] Cacheo de opciones WebAuthn
- [ ] Limpieza automática de desafíos

---

### FASE 10: Auditoría de Documentación

**Estado actual:**
✅ WEBAUTHN_IMPLEMENTATION.md completo
✅ TESTING_WEBAUTHN.md completo
✅ WEBAUTHN_CLI.md completo
✅ IMPLEMENTATION_SUMMARY.md completo
✅ QUICKSTART.md completo

**Recomendaciones:**
1. Agregar diagramas de flujo
2. Agregar ejemplos de código para integración
3. Crear guía de troubleshooting avanzado

---

## 🎯 PROMPTS PARA REFACTORIZACIÓN/CREACIÓN

### Prompt 1: Mejorar Modelos WebAuthn

```markdown
ACTÚA COMO: Desarrollador Senior Django especializado en seguridad FIDO2/WebAuthn

CONTEXTO:
El proyecto DentalPro tiene implementados los modelos WebAuthnCredential y WebAuthnChallenge.
Se requiere mejorar estos modelos con métodos utilitarios y mejores prácticas.

TAREA:
Refactoriza el archivo `/workspace/core/models.py` para:

1. Agregar al modelo WebAuthnCredential:
   - Método `get_active_credentials(user)` que retorne queryset de credenciales activas
   - Método `mark_as_inactive()` para desactivar credencial individual
   - Método `get_device_type_display()` que interprete el AAGUID
   - Property `device_info` que retorne dict con información del dispositivo

2. Agregar al modelo WebAuthnChallenge:
   - Método estático `clean_expired()` que elimine desafíos expirados
   - Método `is_valid()` que verifique si el desafío es usable
   - Método `consume()` que marque el desafío como usado atómicamente
   - Agregar índice compuesto en (user, challenge_type, is_used, expires_at)

3. Mejoras generales:
   - Agregar docstrings completos en español
   - Agregar type hints
   - Agregar logs en métodos críticos
   - Considerar usar transactions donde aplique

RESTRICCIONES:
- Mantener compatibilidad con migraciones existentes
- No cambiar nombres de campos existentes
- Usar español en comentarios y docstrings
- Seguir estilo PEP 8

ENTREGABLE:
Código completo del archivo models.py refactorizado
```

---

### Prompt 2: Mejorar Vistas API con Logging y Rate Limiting

```markdown
ACTÚA COMO: Arquitecto de Software Django especializado en APIs seguras

CONTEXTO:
Las vistas WebAuthn en `/workspace/core/views.py` funcionan correctamente pero carecen de:
- Logging de auditoría
- Rate limiting
- Manejo estructurado de errores
- Headers de seguridad

TAREA:
Refactoriza el archivo `/workspace/core/views.py` para:

1. Implementar logging de auditoría:
   - Crear logger dedicado 'webauthn.audit'
   - Loguear intentos exitosos/fallidos de registro
   - Loguear intentos exitosos/fallidos de autenticación
   - Incluir IP, user-agent, username en logs
   - Loguear detección de clonación como WARNING

2. Implementar rate limiting:
   - Máximo 5 intentos de registro por minuto por IP
   - Máximo 10 intentos de autenticación por minuto por IP
   - Retornar 429 Too Many Requests cuando exceda
   - Usar cache de Django para contadores

3. Mejorar manejo de errores:
   - Crear clase base WebAuthnAPIException
   - Crear excepciones específicas (InvalidChallenge, CredentialNotFound, etc.)
   - Handler global de excepciones
   - Respuestas de error estandarizadas

4. Agregar headers de seguridad:
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - Strict-Transport-Security (si es HTTPS)
   - Content-Security-Policy apropiado

5. Mejoras de código:
   - Extraer lógica repetida a métodos privados
   - Usar async/where where applicable
   - Agregar type hints
   - Docstrings completos

RESTRICCIONES:
- Mantener compatibilidad con frontend existente
- No cambiar estructura de respuestas JSON exitosas
- Rate limiting debe ser configurable desde settings

ENTREGABLE:
Código completo del archivo views.py refactorizado
```

---

### Prompt 3: Crear Middleware de Auditoría WebAuthn

```markdown
ACTÚA COMO: Especialista en Seguridad Django

CONTEXTO:
DentalPro requiere un middleware para auditar todas las operaciones WebAuthn.

TAREA:
Crea un nuevo archivo `/workspace/core/middleware.py` (o extiende el existente) con:

1. Clase `WebAuthnAuditMiddleware`:
   - Interceptar requests a endpoints /core/api/webauthn/*
   - Extraer y loguear: IP, user-agent, timestamp, endpoint
   - Detectar patrones sospechosos (múltiples IPs para mismo usuario)
   - Agregar request ID único para tracing

2. Funcionalidades:
   - GeoIP lookup opcional (si hay librería disponible)
   - Detección de User-Agent spoofing
   - Rate limiting a nivel de middleware
   - Bloqueo temporal de IPs sospechosas

3. Integración con settings:
   - WEBALTHN_AUDIT_ENABLED (bool)
   - WEBAUTHN_RATE_LIMIT (dict)
   - WEBAUTHN_BLOCK_DURATION (timedelta)

4. Signals:
   - webauthn_register_attempt
   - webauthn_authenticate_attempt
   - webauthn_clonation_detected
   - webauthn_rate_limit_exceeded

RESTRICCIONES:
- Middleware debe ser opcional (toggle en settings)
- No impactar rendimiento significativamente
- Logs deben ser asíncronos si es posible

ENTREGABLE:
- Código completo del middleware
- Ejemplo de configuración en settings
- Ejemplo de receivers para signals
```

---

### Prompt 4: Crear Sistema de Backup Codes

```markdown
ACTÚA COMO: Desarrollador Django Security-Focused

CONTEXTO:
Los usuarios de DentalPro pueden perder acceso a su biometría.
Se requiere implementar backup codes como método de recuperación.

TAREA:
Crea los siguientes archivos:

1. `/workspace/core/models.py` - Agregar modelo:
```python
class WebAuthnBackupCode(models.Model):
    user = ForeignKey(User)
    code = CharField(unique=True)  # Hash del código
    code_display = CharField()  # Código legible (solo lectura inicial)
    used_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)
```

2. `/workspace/core/views.py` - Agregar vistas:
   - GenerateBackupCodesView: Genera 10 códigos únicos
   - VerifyBackupCodeView: Verifica y usa un código
   - ListBackupCodesView: Lista códigos no usados
   - RevokeBackupCodeView: Revoca un código específico

3. `/workspace/core/templates/core/backup_codes.html`:
   - UI para generar códigos
   - Mostrar códigos UNA VEZ (advertencia clara)
   - Opción para descargar/imprimir
   - Checkbox de confirmación "Guardé mis códigos"

4. `/workspace/core/forms.py`:
   - BackupCodeGenerationForm
   - BackupCodeVerificationForm

5. Features requeridas:
   - Códigos de 8 caracteres alfanuméricos
   - Hash con bcrypt/argon2 antes de guardar
   - Máximo 10 códigos activos por usuario
   - Expiración opcional (configurable)
   - Logging de generación y uso

RESTRICCIONES:
- Los códigos nunca deben poder leerse después de generados
- UI debe ser clara sobre la importancia de guardar códigos
- Integrar con flujo de login como fallback

ENTREGABLE:
- Todos los archivos completos
- Migración inicial
- Ejemplos de uso en templates
```

---

### Prompt 5: Crear Dashboard de Auditoría WebAuthn

```markdown
ACTÚA COMO: Desarrollador Full-Stack Django + HTMX + Tailwind

CONTEXTO:
Los administradores de DentalPro necesitan un dashboard para monitorear actividad WebAuthn.

TAREA:
Crea un módulo completo de dashboard:

1. `/workspace/core/views.py` - Agregar vistas:
   - WebAuthnDashboardView: Vista principal con estadísticas
   - WebAuthnActivityLogView: Log de actividades (HTMX)
   - WebAuthnUserDetailView: Detalle de usuario específico
   - WebAuthnExportView: Exportar datos (CSV/JSON)

2. `/workspace/core/templates/core/dashboard/webauthn/`:
   - base.html: Layout del dashboard
   - index.html: Vista principal con cards
   - _activity_log.html: Tabla de actividades (parcial HTMX)
   - _user_list.html: Lista de usuarios con credenciales
   - _statistics.html: Gráficos y estadísticas

3. Features del dashboard:
   - Total de usuarios con biometría
   - Credenciales activas/inactivas
   - Intentos fallidos últimos 7 días
   - Dispositivos más comunes
   - Mapa de intentos (si hay GeoIP)
   - Timeline de actividad reciente
   - Alertas de clonación detectada

4. Gráficos (usar Chart.js o similar):
   - Intentos por día (últimos 30 días)
   - Distribución por tipo de dispositivo
   - Tasa de éxito vs fallo
   - Heatmap de horas de actividad

5. Filtros y búsqueda:
   - Por fecha
   - Por usuario
   - Por tipo de evento
   - Por estado (éxito/fallo)

RESTRICCIONES:
- Usar HTMX para carga dinámica
- Tailwind para estilos
- Solo accesible para superusers/staff
- Paginación en listas largas

ENTREGABLE:
- Vistas completas
- Templates completos
- URLs configuradas
- Ejemplo de datos dummy para pruebas
```

---

### Prompt 6: Crear Sistema de Notificaciones WebAuthn

```markdown
ACTÚA COMO: Desarrollador Django especializado en sistemas de notificación

CONTEXTO:
Los usuarios de DentalPro deben ser notificados cuando:
- Se registra un nuevo dispositivo
- Hay un intento fallido de autenticación
- Se detecta posible clonación
- Se generan backup codes

TAREA:
Crea un sistema de notificaciones:

1. `/workspace/core/notifications.py`:
   - WebAuthnNotificationService class
   - Métodos: send_new_device_email, send_failed_attempt_email, etc.

2. `/workspace/core/templates/core/emails/`:
   - new_device_registered.html/txt
   - failed_authentication_attempt.html/txt
   - clonation_detected.html/txt
   - backup_codes_generated.html/txt

3. `/workspace/core/tasks.py` (Celery si está disponible):
   - send_webauthn_notification task
   - scheduled_cleanup task

4. `/workspace/core/signals.py`:
   - Conectar signals de modelos con notificaciones
   - Disparar notificaciones asíncronas

5. Settings requeridos:
   - WEBAUTHN_NOTIFICATION_ENABLED
   - WEBAUTHN_NOTIFICATION_EMAIL_FROM
   - WEBAUTHN_NOTIFY_ON_FAILED_ATTEMPT (bool)
   - WEBAUTHN_NOTIFY_ON_NEW_DEVICE (bool)

RESTRICCIONES:
- Emails deben ser HTML + plain text
- Soportar múltiples backends (email, console, custom)
- Queue system para no bloquear requests
- Templates deben usar Tailwind inline

ENTREGABLE:
- Servicio de notificaciones completo
- Templates de emails
- Signals configurados
- Ejemplo de configuración
```

---

### Prompt 7: Crear Tests Automatizados WebAuthn

```markdown
ACTÚA COMO: QA Engineer especializado en testing Django

CONTEXTO:
DentalPro necesita tests automatizados para el módulo WebAuthn.

TAREA:
Crea una suite completa de tests:

1. `/workspace/core/tests/test_models.py`:
   - Test WebAuthnCredential creation
   - Test WebAuthnChallenge expiration
   - Test clean_expired method
   - Test get_active_credentials
   - Test sign_count increment

2. `/workspace/core/tests/test_views.py`:
   - Test register start view
   - Test register complete view
   - Test authenticate start view
   - Test authenticate complete view
   - Test error cases (invalid challenge, expired, etc.)
   - Test rate limiting
   - Test clonation detection

3. `/workspace/core/tests/test_middleware.py`:
   - Test audit logging
   - Test rate limiting middleware
   - Test IP blocking

4. `/workspace/core/tests/test_commands.py`:
   - Test webauthn list command
   - Test webauthn stats command
   - Test webauthn clean-challenges command
   - Test webauthn disable command

5. `/workspace/core/tests/test_integration.py`:
   - Full registration flow
   - Full authentication flow
   - Backup codes flow
   - Multi-device scenarios

6. Fixtures requeridas:
   - test_users.json
   - test_credentials.json
   - mock_webauthn_responses.py

RESTRICCIONES:
- Cobertura mínima 90%
- Usar pytest-django si es posible
- Mockear llamadas externas (WebAuthn library)
- Tests deben ser independientes
- Incluir tests de seguridad

ENTREGABLE:
- Todos los archivos de test
- Fixtures
- Script para correr tests
- Reporte de cobertura esperado
```

---

### Prompt 8: Crear Documentación Técnica Avanzada

```markdown
ACTÚA COMO: Technical Writer especializado en documentación de APIs

CONTEXTO:
DentalPro requiere documentación técnica avanzada para desarrolladores.

TAREA:
Crea los siguientes documentos:

1. `/workspace/docs/webauthn/architecture.md`:
   - Diagrama de arquitectura
   - Flujo de registro paso a paso
   - Flujo de autenticación paso a paso
   - Componentes y responsabilidades
   - Secuencia de mensajes

2. `/workspace/docs/webauthn/api-reference.md`:
   - Endpoint: POST /api/webauthn/register/start/
   - Endpoint: POST /api/webauthn/register/complete/
   - Endpoint: POST /api/webauthn/authenticate/start/
   - Endpoint: POST /api/webauthn/authenticate/complete/
   - Request/Response schemas
   - Error codes
   - Ejemplos curl

3. `/workspace/docs/webauthn/security-guide.md`:
   - Mejores prácticas de seguridad
   - Configuración recomendada
   - Hardening del servidor
   - Monitoreo y alertas
   - Incident response plan

4. `/workspace/docs/webauthn/troubleshooting.md`:
   - Errores comunes y soluciones
   - Debugging guide
   - Logs interpretation
   - Browser compatibility issues
   - FAQ

5. `/workspace/docs/webauthn/deployment.md`:
   - Requisitos de producción
   - Configuración HTTPS
   - Load balancing considerations
   - Backup y recovery
   - Scaling strategies

RESTRICCIONES:
- Usar Markdown con sintaxis consistente
- Incluir diagramas Mermaid cuando aplique
- Ejemplos de código verificables
- Enlazar entre documentos
- Versión del documento

ENTREGABLE:
- 5 documentos completos en formato Markdown
- Índice general
- Glosario de términos
```

---

## 📊 MATRIZ DE PRIORIDADES

| Prioridad | Fase | Impacto | Esfuerzo | Estado |
|-----------|------|---------|----------|--------|
| ALTA | FASE 1 | Seguridad | Bajo | ✅ Completo |
| ALTA | FASE 2 | Seguridad | Medio | ⚠️ Pendiente |
| ALTA | Prompt 2 | Seguridad | Alto | 🔴 Por hacer |
| ALTA | Prompt 7 | Calidad | Alto | 🔴 Por hacer |
| MEDIA | Prompt 1 | Mantenibilidad | Medio | 🔴 Por hacer |
| MEDIA | Prompt 4 | UX/Seguridad | Medio | 🔴 Por hacer |
| MEDIA | Prompt 6 | UX | Medio | 🔴 Por hacer |
| BAJA | Prompt 3 | Seguridad | Bajo | 🔴 Por hacer |
| BAJA | Prompt 5 | Admin | Alto | 🔴 Por hacer |
| BAJA | Prompt 8 | Docs | Medio | 🔴 Por hacer |

---

## 🚀 PLAN DE EJECUCIÓN

### Semana 1: Seguridad Crítica
1. Ejecutar Prompt 2 (Logging + Rate Limiting)
2. Ejecutar Prompt 7 (Tests)
3. Validar con VALIDATION.md

### Semana 2: Mejoras de Modelo
1. Ejecutar Prompt 1 (Mejorar Modelos)
2. Ejecutar Prompt 4 (Backup Codes)
3. Actualizar documentación

### Semana 3: Monitoreo y Notificaciones
1. Ejecutar Prompt 3 (Middleware)
2. Ejecutar Prompt 6 (Notificaciones)
3. Configurar alerts

### Semana 4: Dashboard y Documentación
1. Ejecutar Prompt 5 (Dashboard)
2. Ejecutar Prompt 8 (Documentación)
3. Auditoría final

---

## ✅ CHECKLIST DE VALIDACIÓN FINAL

- [ ] Todos los tests pasan (pytest)
- [ ] Coverage > 90%
- [ ] No hay vulnerabilidades críticas (bandit/safety)
- [ ] Performance acceptable (<200ms para endpoints WebAuthn)
- [ ] Documentación actualizada
- [ ] Migration tests pasan
- [ ] Integration tests pasan
- [ ] Security audit passed

---

**Documento creado:** Mayo 29, 2024
**Próxima revisión:** Junio 5, 2024
**Responsable:** Equipo de Desarrollo DentalPro