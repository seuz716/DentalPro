# DentalPro
> Software de gestión odontológica local. Offline-first. Hecho en Colombia para consultorios independientes.

---

## 📖 ¿Qué es DentalPro?
DentalPro es un sistema clínico completo que se instala directamente en tu computador. **No requiere internet para funcionar**, no cobra suscripciones mensuales y guarda toda la información de tu consultorio de forma local y segura. 

Está diseñado para que el odontólogo pierda menos tiempo en papeleo y más tiempo atendiendo. El sistema traduce automáticamente términos técnicos a un lenguaje claro que el paciente entiende al instante.

---

## ✨ Características Principales
| Función | Qué hace | Para qué sirve |
|---|---|---|
| 🖥️ **100% Local** | Funciona sin conexión a internet | Evita caídas de red y protege la privacidad |
| 🦷 **Odontograma SVG** | Gráfico interactivo de los 32 dientes | Marca estados con un clic, sin dibujos manuales |
| 📋 **Historia Clínica** | Registro digital + traducción a lenguaje humano | El paciente entiende su diagnóstico sin googlear |
| 🔍 **Búsqueda Instantánea** | Filtra por nombre, cédula o teléfono sin recargar | Encuentra cualquier ficha en menos de 1 segundo |
| 📅 **Gestión de Citas** | Calendario, estados y recordatorios | Reduce ausencias y organiza la jornada |
| 📦 **Inventario** | Control de materiales con alertas de stock mínimo | Nunca te quedas sin insumos a mitad de procedimiento |
| 💰 **Finanzas & DIAN** | Facturación interna y exportación de datos | Cumple con reportes tributarios sin software extra |
| 🤖 **Asistente IA** *(Opcional)* | Interpretación de notas y resúmenes clínicos | Solo se activa si hay internet. Tus datos no se guardan en la nube |

---

## 🛠️ Stack Tecnológico (y por qué lo usamos)
| Tecnología | Rol en el proyecto | Explicación sencilla |
|---|---|---|
| **Django 4.2** | Motor principal | Organiza datos, usuarios y seguridad de forma probada y estable |
| **SQLite** | Base de datos | Archivo local `.sqlite3`. No requiere instalación ni servidores |
| **HTMX 1.9** | Interfaz dinámica | Hace que los botones y formularios respondan al instante sin JavaScript complejo |
| **Tailwind CSS 3** | Diseño visual | Estilo moderno, limpio y adaptable a cualquier pantalla |
| **Python 3.11** | Lenguaje base | Rápido, legible y con librerías maduras para escritorio |
| **PyInstaller** | Empaquetado final | Convierte el código en un `.exe` instalable en Windows |

---

## 🚀 Instalación

### 👨‍💻 Para desarrolladores (entorno de pruebas)
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/dentalpro.git
cd dentalpro

# 2. Crear entorno aislado
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Preparar base de datos y crear usuario administrador
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev

# 5. Iniciar servidor local
python manage.py runserver --settings=config.settings.dev
```
🌐 Abre `http://127.0.0.1:8000` en tu navegador.

### 💼 Para consultorios (instalador final)
*Disponible al completar la Fase 13.* Se entregará un archivo `DentalPro_Setup.exe` que instala la aplicación, crea la base de datos automáticamente y abre el programa al hacer doble clic. No se requiere Python ni conocimientos técnicos.

---

## 📁 Estructura del Proyecto
```
dentalpro/
├── config/           # Ajustes generales, rutas y seguridad
├── core/             # Plantillas base, estilos comunes y utilidades
├── pacientes/        # Fichas, historia clínica y odontograma
├── citas/            # Calendario y recordatorios
├── inventario/       # Control de materiales y alertas
├── finanzas/         # Facturación y exportación DIAN
├── media/            # Radiografías y fotos clínicas (almacenamiento local)
├── templates/        # Interfaz visual (HTML + Tailwind + HTMX)
└── db.sqlite3        # Base de datos local (se crea sola)
```
Cada módulo es independiente pero se comunica entre sí. Si un día necesitas extraer o respaldar datos, solo copias `db.sqlite3` y la carpeta `media/`.

---

## 🧭 Filosofía de Diseño
1. **Offline-First**: El consultorio no se detiene porque falle el wifi.
2. **Privacidad Real**: Los datos nunca salen de tu PC, salvo que tú actives explícitamente IA, correo o WhatsApp.
3. **Lenguaje Claro**: El sistema convierte `"caries oclusal en pieza 36"` en `"pequeña caries en muela inferior izquierda"`.
4. **Sin Dependencias Ocultas**: No requiere nube, licencias mensuales ni servidores externos.

---

## 🗺️ Hoja de Ruta (Roadmap)
- [x] Fase 0: Estructura Django, Settings dev/prod
- [x] Fase 1: Modelo `Patient` con validación de cédula
- [x] Fase 2: Admin customizado y migraciones
- [x] Fase 3: Vistas CBV (ListView, DetailView) + búsqueda
- [x] Fase 4: Templates base y listado con Tailwind + HTMX
- [x] Fase 5: Odontograma SVG (Sistema FDI)
- [x] Fase 10: One-Click Launcher para escritorio
- [ ] Fase 6: Módulo de citas y calendario
- [ ] Fase 7: Inventario con alertas de stock crítico
- [ ] Fase 8: Finanzas y exportación para portal DIAN
- [ ] Fase 9: Asistente IA (Anthropic) con traducción clínica
- [ ] Fase 11: Notificaciones por email y WhatsApp
- [ ] Fase 12: Portal web limitado para pacientes
- [ ] Fase 13: Dashboard con gráficos y reportes reales

---

## 🚀 Launcher de Escritorio (Fase 10)

### Para Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements/dev.txt

# Iniciar servidor
python manage.py runserver --settings=config.settings.dev
```

Accede a `http://127.0.0.1:8000`

### One-Click Launcher (Producción)

```bash
# Instalar dependencias de producción
pip install -r requirements/prod.txt

# Ejecutar el launcher
python desktop/launcher.py
```

El launcher automáticamente:
- ✓ Configura Django con settings de producción
- ✓ Inicia servidor Waitress en `http://localhost:8000`
- ✓ Abre navegador web automáticamente
- ✓ Maneja cierre limpio (Ctrl+C)

### Crear Ejecutable Independiente

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable (one-file)
pyinstaller dentalpro.spec

# El archivo estará en: dist/DentalPro
```

Luego puedes distribuir `dist/DentalPro` a usuarios sin requería Python instalado.

---

## 📜 Licencia y Uso
Licencia **MIT**. Uso libre para consultorios independientes y profesionales de la salud.  
⚠️ No está permitido redistribuir el software como servicio SaaS, plataforma multiusuario en la nube o producto comercial sin autorización expresa del autor.

---

## 📬 Soporte y Contribuciones
- 🐛 ¿Encontraste un error? Abre un `Issue` con descripción, pasos para reproducir y versión de Python.
- 💡 ¿Tienes una mejora? Envía un `Pull Request` siguiendo la convención de commits y comentarios en español.
- 📩 Contacto técnico: `[correo@ejemplo.com]` | WhatsApp: `+[57] XXX XXX XXXX`

---
`DentalPro v1.0-alpha` • Hecho con Python, Django y sentido común para la odontología colombiana.