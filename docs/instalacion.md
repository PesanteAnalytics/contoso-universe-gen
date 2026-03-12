# Instalación

> Guía de instalación de Contoso Universe Generator (CUG).

---

## Prerequisitos

| Requisito | Versión mínima | Notas |
|-----------|---------------|-------|
| **Python** | 3.12+ | Recomendado: usar `uv` para gestión de entornos |
| **pip** o **uv** | Última estable | `uv` es más rápido para resolver dependencias |
| **ODBC Driver** | Driver 17 o 18 | Solo si vas a usar formato `sqlserver` |
| **SQL Server** | Express 2019+ | Solo si vas a usar formato `sqlserver` |

---

## Instalación Estándar (pip)

```bash
# Clonar el repositorio
git clone https://github.com/Support1-PAL/contoso-universe-gen.git
cd contoso-universe-gen

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar en modo editable
pip install -e .

# Verificar instalación
cug --help
```

---

## Instalación con uv (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/Support1-PAL/contoso-universe-gen.git
cd contoso-universe-gen

# Crear entorno virtual con uv
uv venv .venv --python 3.12

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar con uv
uv pip install -e .

# Verificar instalación
cug --help
```

---

## Dependencias

CUG instala automáticamente las siguientes dependencias:

| Paquete | Propósito |
|---------|-----------|
| `polars` | Motor de DataFrames de alta velocidad |
| `duckdb` | Base de datos analítica embebida |
| `faker` | Generación de nombres, direcciones y datos ficticios |
| `pydantic` | Validación de configuración |
| `typer` | Framework para CLI |
| `rich` | Salida de consola con formato enriquecido |
| `pyodbc` | Conexión a SQL Server vía ODBC |
| `deltalake` | Escritura de tablas Delta Lake |
| `openpyxl` | Escritura de archivos Excel (.xlsx) |

---

## Instalación del Driver ODBC (solo para SQL Server)

Si planeas exportar datos a SQL Server, necesitas instalar un driver ODBC.

### Windows

1. Descargar desde [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Instalar **ODBC Driver 17** o **ODBC Driver 18** for SQL Server
3. Verificar la instalación:

```python
import pyodbc
print(pyodbc.drivers())
# Debería incluir 'ODBC Driver 17 for SQL Server' o similar
```

### Drivers soportados (en orden de preferencia)

1. `ODBC Driver 18 for SQL Server` — El más reciente
2. `ODBC Driver 17 for SQL Server` — Ampliamente disponible
3. `SQL Server Native Client 11.0` — Legacy, funcional

> [!NOTE]
> CUG auto-detecta el mejor driver disponible. No necesitas configurar nada manualmente a menos que tengas requisitos específicos.

> [!IMPORTANT]
> El ODBC Driver 18 requiere SSL por defecto. Para desarrollo local, CUG agrega automáticamente `TrustServerCertificate=yes` a la cadena de conexión.

---

## Verificar la Instalación

```bash
# Ver ayuda general
cug --help

# Ver idiomas disponibles
cug info

# Ver formatos de salida
cug formats

# Ver categorías de productos
cug categories

# Generación rápida de prueba (~5K órdenes)
cug generate -c configs/quicktest.toml
```

Si todos los comandos funcionan correctamente, la instalación está completa.

---

## Invocación Alternativa

Si no instalaste con `pip install -e .`, puedes invocar CUG directamente con:

```bash
# Desde el directorio raíz del proyecto
.venv\Scripts\python.exe -m cug generate [OPTIONS]
```

---

## Solución de Problemas Comunes

### `ModuleNotFoundError: No module named 'cug'`

Asegúrate de haber instalado con `pip install -e .` desde el directorio raíz del proyecto.

### `ImportError: No module named 'pyodbc'`

```bash
pip install pyodbc
```

Si falla en Windows, verifica que Visual C++ Build Tools estén instalados.

### `UnicodeEncodeError` al ejecutar CUG

CUG utiliza caracteres Unicode para la interfaz Rich. Asegúrate de que tu terminal soporte UTF-8:

```powershell
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

---

← [Volver al índice](README.md)
