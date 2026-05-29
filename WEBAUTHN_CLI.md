# Comandos WebAuthn CLI

Gestiona credenciales y desafíos WebAuthn desde la línea de comandos.

## Uso Básico

```bash
python manage.py webauthn [subcommando] [opciones]
```

## Subcomandos

### 1. Listar Credenciales

```bash
# Listar todas las credenciales
python manage.py webauthn list

# Listar credenciales de un usuario específico
python manage.py webauthn list --user=usuario

# Listar solo credenciales activas
python manage.py webauthn list --active

# Combinar opciones
python manage.py webauthn list --user=usuario --active
```

### 2. Desactivar Credencial

```bash
# Desactivar una credencial por ID
python manage.py webauthn disable [credential_id]

# Obtener el ID de una credencial
python manage.py webauthn list  # Busca el ID en los resultados
```

### 3. Limpiar Desafíos Expirados

```bash
# Eliminar todos los desafíos expirados
python manage.py webauthn clean-challenges
```

### 4. Información de Usuario

```bash
# Ver todas las credenciales de un usuario
python manage.py webauthn user-info usuario

# Incluye:
# - Información de cuenta
# - Lista de credenciales
# - Desafíos pendientes
```

### 5. Estadísticas

```bash
# Ver estadísticas generales
python manage.py webauthn stats

# Muestra:
# - Total de usuarios con credenciales
# - Total y estado de credenciales
# - Desafíos pendientes y expirados
# - Dispositivos más usados (Top 5)
```

## Ejemplos Prácticos

### Auditoría de Seguridad

```bash
# Ver todas las credenciales activas
python manage.py webauthn list --active

# Ver credenciales de un usuario específico
python manage.py webauthn user-info juan_perez

# Ver desafíos pendientes (pueden indicar autenticaciones incompletas)
python manage.py webauthn stats
```

### Mantenimiento

```bash
# Limpiar base de datos de desafíos expirados
python manage.py webauthn clean-challenges

# Verificar estadísticas después de la limpieza
python manage.py webauthn stats
```

### Administración de Usuarios

```bash
# Desactivar una credencial comprometida
python manage.py webauthn disable eNqNVEtuwyAM_ZWKcwYlgOk6TtNJ3bRqVx6SMDvSbBPkNlW37l0TaRZNAoP97H8/sLpnXwlm/2qVJ1+EsvY0CvwZ5PwzZ3VXTX...

# Verificar que se desactivó
python manage.py webauthn user-info usuario
```

## Output de Ejemplo

### Lista de Credenciales
```
Usuario  │ Dispositivo        │ Activa │ Sign Count │ Creada            │ Última vez
─────────┼────────────────────┼────────┼────────────┼───────────────────┼───────────────
admin    │ Windows Hello      │ ✓      │ 5          │ 2024-05-20 10:30  │ 2024-05-29 15:45
pedro    │ Touch ID / Face ID │ ✓      │ 12         │ 2024-05-15 14:20  │ 2024-05-28 09:30
maria    │ Android Biometric  │ ✗      │ 3          │ 2024-05-10 11:00  │ 2024-05-15 16:00
```

### Información de Usuario
```
=== Usuario: admin ===
Email: admin@dentalpro.local
Nombre completo: Administrador DentalPro

=== Credenciales (2) ===
Dispositivo        │ Activa │ Sign Count │ Creada            │ Última vez        │ AAGUID
───────────────────┼────────┼────────────┼───────────────────┼───────────────────┼──────────
Windows Hello      │ ✓      │ 5          │ 2024-05-20 10:30  │ 2024-05-29 15:45  │ 4e4e40de...
Laptop Backup Key  │ ✓      │ 8          │ 2024-05-21 09:15  │ 2024-05-28 14:30  │ bb8a8c01...
```

### Estadísticas
```
=== Estadísticas WebAuthn ===
Usuarios con credenciales: 23
Total de credenciales: 47
  - Activas: 45
  - Inactivas: 2

Desafíos pendientes: 1
Desafíos expirados: 5

=== Dispositivos Top 5 ===
Windows Hello: 18
Touch ID / Face ID: 14
Android Biometric: 10
Windows Biometric: 3
Security Key: 2
```

## Automatización

### Limpiar desafíos expirados regularmente (Cron)

```bash
# Agregar a crontab
0 */6 * * * cd /home/cesar/mis_proyectos/DentalPro && source .venv/bin/activate && python manage.py webauthn clean-challenges

# Para cada 6 horas
*/6 * * * *  # Cada 6 horas
0 * * * *    # Cada hora
0 0 * * *    # Cada día
```

### Usando Celery (si está disponible)

```python
# tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def cleanup_expired_challenges():
    call_command('webauthn', 'clean-challenges')
```

## Troubleshooting

### Comando no encontrado

```bash
# Verificar que el archivo está en el lugar correcto
ls -la core/management/commands/webauthn.py

# Ejecutar colectsync (si es necesario)
python manage.py collectstatic
```

### Permisos insuficientes

```bash
# Ejecutar con el usuario correcto
sudo -u www-data python manage.py webauthn stats

# O con virtualenv
source .venv/bin/activate && python manage.py webauthn stats
```

### Base de datos vacía

```bash
# Ejecutar migraciones
python manage.py migrate

# Verificar que las tablas existen
python manage.py dbshell
> SELECT * FROM core_webauthnidentity LIMIT 1;
```
